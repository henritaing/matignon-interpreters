#!/usr/bin/env python3
'''Entry point. Reads a split CSV, builds 2-minute windows from subtitle files,
classifies each window with the Claude API, and writes a results CSV.'''

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from claude_api import read_prompt_file, run_classification, write_output
from windowing import build_all_windows, print_stats

load_dotenv()


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {c: c.strip().lower().replace(" ", "_") for c in df.columns}
    df = df.rename(columns=mapping)
    required = {"video_id", "segment_index", "segment_start", "segment_end"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"split CSV missing columns: {sorted(missing)}")
    return df


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split-csv", required=True, type=Path)
    parser.add_argument("--split-name", required=True)
    parser.add_argument("--subtitles-dir", type=Path, default=Path("data/subtitles"))
    parser.add_argument("--prompt", type=Path, default=Path("prompt_theme_v1.txt"))
    parser.add_argument("--out-dir", type=Path, default=Path("out"))
    parser.add_argument("--model", default="claude-sonnet-4-6")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--dry-run", action="store_true",
                        help="build windows, report coverage and cost, make no API calls")
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    system_prompt, prompt_hash = read_prompt_file(args.prompt)

    df = pd.read_csv(args.split_csv, sep=None, engine="python")
    df = standardize_columns(df)

    windows, stats = build_all_windows(df, args.subtitles_dir)
    print_stats(stats, windows, args.split_name)

    if args.dry_run:
        total_chars = sum(len(w.text) for w in windows)
        print(f"  transcript chars    : {total_chars} (~{total_chars // 4} input tokens, "
              f"plus ~{len(system_prompt) // 4} prompt tokens per call)")
        return 0

    from anthropic import Anthropic

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY is not set", file=sys.stderr)
        return 1

    client = Anthropic()
    cache = run_classification(
        windows, client, args.model, system_prompt, prompt_hash,
        args.split_name, args.out_dir, args.workers,
    )
    write_output(windows, cache, prompt_hash, args.model, args.out_dir, args.split_name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
