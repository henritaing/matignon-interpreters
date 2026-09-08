from __future__ import annotations

import hashlib
import json
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from config import THEMES, VALID_SHARES, MIN_CHARS, MAX_RETRIES
from timestamps import format_timestamp
from windowing import Window


# --------------------------------------------------------------------------
# Cache
# --------------------------------------------------------------------------

class ResultCache:
    def __init__(self, path: Path):
        self.path = path
        self.lock = threading.Lock()
        self.done: dict[str, dict] = {}
        if path.exists():
            with path.open(encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    row = json.loads(line)
                    if row.get("api_error") is None:
                        self.done[row["cache_key"]] = row

    def append(self, row: dict) -> None:
        with self.lock:
            with self.path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            if row.get("api_error") is None:
                self.done[row["cache_key"]] = row


# --------------------------------------------------------------------------
# API helpers
# --------------------------------------------------------------------------

def read_prompt_file(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8")
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def parse_json_from_reply(text: str) -> dict:
    """Parse the model reply, tolerating stray fences or surrounding text."""
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    json_start, json_end = cleaned.find("{"), cleaned.rfind("}")
    if json_start == -1 or json_end <= json_start:
        raise ValueError(f"no JSON object in reply: {text[:200]!r}")
    return json.loads(cleaned[json_start:json_end + 1])


def validate_api_response(payload: dict) -> dict:
    label = payload.get("label")
    if label not in THEMES:
        raise ValueError(f"invalid label: {label!r}")
    rule = payload.get("rule")
    if rule is not None and rule not in range(1, 9):
        raise ValueError(f"invalid rule: {rule!r}")
    share = payload.get("dominant_share")
    if share not in VALID_SHARES:
        share = None
    runner_up = payload.get("runner_up")
    if runner_up not in THEMES:
        runner_up = None
    confidence = payload.get("confidence")
    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = None
    return {
        "label": label,
        "rule": rule,
        "dominant_share": share,
        "boilerplate": bool(payload.get("boilerplate", False)),
        "runner_up": runner_up,
        "confidence": confidence,
    }


def ask_claude_to_classify(client, model: str, system_prompt: str, window: Window) -> dict:
    """One API call with retry. Returns a validated result dict."""
    user_message = (
        "<window>\n"
        f"id: {window.window_id}\n"
        "transcript:\n"
        f"{window.text}\n"
        "</window>"
    )
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=300,
                temperature=0,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )
            reply = "".join(b.text for b in response.content if b.type == "text")
            result = validate_api_response(parse_json_from_reply(reply))
            result["api_error"] = None
            result["input_tokens"] = response.usage.input_tokens
            result["output_tokens"] = response.usage.output_tokens
            return result
        except Exception as exc:  # noqa: BLE001 - retry on transport and parse errors alike
            last_error = exc
            time.sleep(min(2 ** attempt, 30))
    return {
        "label": None,
        "rule": None,
        "dominant_share": None,
        "boilerplate": None,
        "runner_up": None,
        "confidence": None,
        "api_error": f"{type(last_error).__name__}: {last_error}",
        "input_tokens": None,
        "output_tokens": None,
    }


# --------------------------------------------------------------------------
# Classification pipeline
# --------------------------------------------------------------------------

def make_cache_key(window_id: str, prompt_hash: str, model: str) -> str:
    return f"{window_id}|{prompt_hash}|{model}"


def process_window(
    window: Window,
    client,
    model: str,
    system_prompt: str,
    prompt_hash: str,
    split_name: str,
    cache: ResultCache,
) -> dict:
    if len(window.text) < MIN_CHARS:
        result = {
            "label": "indéterminé", "rule": None, "dominant_share": "<50%",
            "boilerplate": False, "runner_up": None, "confidence": None,
            "api_error": None, "input_tokens": 0, "output_tokens": 0,
        }
    else:
        result = ask_claude_to_classify(client, model, system_prompt, window)
    row = {
        "cache_key": make_cache_key(window.window_id, prompt_hash, model),
        "split": split_name,
        **{k: v for k, v in asdict(window).items() if k != "text"},
        "window_start_hms": format_timestamp(window.window_start),
        "window_end_hms": format_timestamp(window.window_end),
        "n_chars": len(window.text),
        "model": model,
        "prompt_hash": prompt_hash,
        **result,
    }
    cache.append(row)
    return row


def run_classification(
    windows: list[Window],
    client,
    model: str,
    system_prompt: str,
    prompt_hash: str,
    split_name: str,
    out_dir: Path,
    workers: int,
) -> ResultCache:
    cache = ResultCache(out_dir / f"{split_name}_cache.jsonl")
    todo = [w for w in windows if make_cache_key(w.window_id, prompt_hash, model) not in cache.done]
    print(f"  cached              : {len(windows) - len(todo)}")
    print(f"  to classify         : {len(todo)}")

    if todo:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {
                pool.submit(process_window, w, client, model, system_prompt, prompt_hash, split_name, cache): w
                for w in todo
            }
            for i, future in enumerate(as_completed(futures), 1):
                future.result()
                if i % 25 == 0 or i == len(todo):
                    print(f"  {i}/{len(todo)}", flush=True)

    return cache


def write_output(
    windows: list[Window],
    cache: ResultCache,
    prompt_hash: str,
    model: str,
    out_dir: Path,
    split_name: str,
) -> None:
    rows = [
        cache.done[make_cache_key(w.window_id, prompt_hash, model)]
        for w in windows
        if make_cache_key(w.window_id, prompt_hash, model) in cache.done
    ]
    failed = len(windows) - len(rows)
    output_df = pd.DataFrame(rows)
    columns = [
        "split", "window_id", "video_id", "segment_index",
        "window_start_hms", "window_end_hms", "window_start", "window_end",
        "label", "rule", "dominant_share", "boilerplate", "runner_up", "confidence",
        "n_cues", "n_chars", "model", "prompt_hash",
    ]
    output_df = output_df[[c for c in columns if c in output_df.columns]]
    out_path = out_dir / f"{split_name}_windows.csv"
    output_df.to_csv(out_path, index=False, encoding="utf-8")

    print(f"\nwrote {out_path} ({len(output_df)} rows, {failed} failed)")
    if not output_df.empty:
        print("\nlabel distribution:")
        print(output_df["label"].value_counts().to_string())
        n_boilerplate = int(output_df["boilerplate"].fillna(False).astype(bool).sum())
        print(f"\nboilerplate windows : {n_boilerplate} ({100 * n_boilerplate / len(output_df):.1f}%)")
        n_undetermined = int((output_df["label"] == "indéterminé").sum())
        print(f"indéterminé windows : {n_undetermined} ({100 * n_undetermined / len(output_df):.1f}%)")
