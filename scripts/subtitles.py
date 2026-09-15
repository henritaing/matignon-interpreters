'''Subtitle parsing for standard SRT files.'''

import glob
import re
from dataclasses import dataclass
from pathlib import Path

from timestamps import parse_timestamp


@dataclass
class Cue:
    start: float
    end: float
    text: str


SRT_BLOCK_PATTERN = re.compile(r"""
    (?P<idx>\d+)\s+                                             # block number
    (?P<start>\d{1,2}:\d{2}:\d{2}[,.]\d{1,3})                  # start timestamp HH:MM:SS,mmm
    \s*-->\s*
    (?P<end>\d{1,2}:\d{2}:\d{2}[,.]\d{1,3})                    # end timestamp
    \s+
    (?P<text>.*?)                                               # subtitle text (lazy, multi-line)
    (?=\s*\d+\s+\d{1,2}:\d{2}:\d{2}[,.]\d{1,3}\s*-->|\s*$)    # lookahead: next block or end of file
""", re.DOTALL | re.VERBOSE)


def parse_subtitles(path: Path) -> list[Cue]:
    file_text = path.read_text(encoding="utf-8-sig", errors="replace")
    cues = []
    for match in SRT_BLOCK_PATTERN.finditer(file_text):
        text = " ".join(match.group("text").split())
        if not text:
            continue
        cues.append(
            Cue(parse_timestamp(match.group("start")), parse_timestamp(match.group("end")), text)
        )
    if not cues:
        raise ValueError(f"{path.name}: no SRT cue parsed")
    return cues


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
