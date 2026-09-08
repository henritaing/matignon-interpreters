from __future__ import annotations

import glob
import re
from dataclasses import dataclass
from pathlib import Path

from timestamps import parse_timestamp, seconds_to_english


@dataclass
class Cue:
    start: float
    end: float
    text: str


# Two subtitle formats are supported:
#   - Standard SRT blocks (index + timestamp range + text)
#   - Transcript format: one line per cue, starting with a timestamp and a human-readable duration

SRT_BLOCK_PATTERN = re.compile(r"""
    (?P<idx>\d+)\s+                                             # block number
    (?P<start>\d{1,2}:\d{2}:\d{2}[,.]\d{1,3})                  # start timestamp HH:MM:SS,mmm
    \s*-->\s*
    (?P<end>\d{1,2}:\d{2}:\d{2}[,.]\d{1,3})                    # end timestamp
    \s+
    (?P<text>.*?)                                               # subtitle text (lazy, multi-line)
    (?=\s*\d+\s+\d{1,2}:\d{2}:\d{2}[,.]\d{1,3}\s*-->|\s*$)    # lookahead: next block or end of file
""", re.DOTALL | re.VERBOSE)

TRANSCRIPT_LINE_PATTERN = re.compile(r"^(?P<ts>\d{1,2}:\d{2}(?::\d{2})?)(?P<rest>.*)$")
HUMAN_DURATION_PATTERN = re.compile(
    r"^(?:\d+\s+hours?,?\s*)?(?:\d+\s+minutes?,?\s*)?(?:\d+\s+seconds?)?"
)

TRANSCRIPT_TAIL_SECONDS = 5.0


def parse_subtitles(path: Path) -> tuple[list[Cue], str]:
    file_text = path.read_text(encoding="utf-8-sig", errors="replace")

    if "-->" in file_text:
        cues = []
        for match in SRT_BLOCK_PATTERN.finditer(file_text):
            text = " ".join(match.group("text").split())
            if not text:
                continue
            cues.append(
                Cue(parse_timestamp(match.group("start")), parse_timestamp(match.group("end")), text)
            )
        if not cues:
            raise ValueError(f"{path.name}: contains '-->' but no cue parsed")
        subtitle_format = "srt_blocks" if file_text.count("\n") > len(cues) else "srt_oneline"
        return cues, subtitle_format

    # Transcript format: each line starts with a timestamp followed by a human-readable duration
    cue_entries: list[tuple[float, str]] = []
    for line in file_text.splitlines():
        line = line.strip()
        if not line:
            continue
        match = TRANSCRIPT_LINE_PATTERN.match(line)
        if not match:
            continue
        seconds = parse_timestamp(match.group("ts"))
        rest = match.group("rest")
        expected_duration = seconds_to_english(int(round(seconds)))
        if rest.startswith(expected_duration):
            text = rest[len(expected_duration):]
        else:
            # Fallback: strip whatever human-readable duration is there.
            text = HUMAN_DURATION_PATTERN.sub("", rest, count=1)
        text = " ".join(text.split())
        if text:
            cue_entries.append((seconds, text))

    if not cue_entries:
        raise ValueError(f"{path.name}: no cue parsed (unknown format)")

    cues = []
    for i, (start, text) in enumerate(cue_entries):
        end = cue_entries[i + 1][0] if i + 1 < len(cue_entries) else start + TRANSCRIPT_TAIL_SECONDS
        cues.append(Cue(start, max(end, start), text))
    return cues, "start_only"


def find_subtitle_file(subtitles_dir: Path, video_id: str) -> Path:
    """Match '<video_id>_clip_subtitles.fr' and near variants, unambiguously."""
    candidates: list[Path] = []
    for pattern in (
        f"{video_id}_clip_subtitles.fr",
        f"{video_id}_clip_subtitles.fr.srt",
        f"{video_id}_clip_subtitles.srt",
        f"{video_id}.srt",
        f"{video_id}_*",
    ):
        candidates.extend(Path(p) for p in glob.glob(str(subtitles_dir / pattern)))
        if candidates:
            break
    # A prefix glob can catch a longer video id; keep only exact-prefix matches.
    candidates = [
        c for c in dict.fromkeys(candidates)
        if c.name == video_id or c.name.startswith(video_id + "_") or c.name.startswith(video_id + ".")
    ]
    if not candidates:
        raise FileNotFoundError(f"no subtitle file for video_id={video_id!r} in {subtitles_dir}")
    if len(candidates) > 1:
        raise ValueError(
            f"ambiguous subtitle files for {video_id!r}: {[c.name for c in candidates]}"
        )
    return candidates[0]
