'''Windowing logic for cutting subtitle segments into fixed windows.'''

import sys
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from config import WINDOW_SECONDS, DROP_TAIL, MIN_CHARS
from subtitles import Cue, find_subtitle_file, parse_subtitles
from timestamps import parse_timestamp


@dataclass
class Window:
    window_id: str
    video_id: str
    segment_index: str
    window_start: float
    window_end: float
    text: str
    n_cues: int


@dataclass
class BuildStats:
    segments: int = 0
    segments_too_short: int = 0
    dropped_seconds: float = 0.0
    kept_seconds: float = 0.0
    empty_windows: int = 0
    formats: dict = field(default_factory=dict)
    file_errors: list = field(default_factory=list)


def build_windows(
    cues: list[Cue],
    video_id: str,
    segment_index: str,
    segment_start: float,
    segment_end: float,
) -> tuple[list[Window], float]:
    """Cut [segment_start, segment_end) into fixed windows. Returns (windows, dropped_seconds).

    A cue is assigned to the window containing its start time, so no cue text is
    duplicated across windows and boundary-spanning cues are not split.
    """
    windows: list[Window] = []
    num_windows = int((segment_end - segment_start) // WINDOW_SECONDS)
    dropped_seconds = (segment_end - segment_start) - num_windows * WINDOW_SECONDS
    if not DROP_TAIL and dropped_seconds > 0:
        num_windows += 1
        dropped_seconds = 0.0

    for i in range(num_windows):
        window_start = segment_start + i * WINDOW_SECONDS
        window_end = min(window_start + WINDOW_SECONDS, segment_end)
        cues_in_window = [c for c in cues if window_start <= c.start < window_end]
        windows.append(
            Window(
                window_id=f"{segment_index}_w{i + 1}",
                video_id=video_id,
                segment_index=segment_index,
                window_start=window_start,
                window_end=window_end,
                text=" ".join(c.text for c in cues_in_window).strip(),
                n_cues=len(cues_in_window),
            )
        )
    return windows, dropped_seconds


def build_all_windows(df: pd.DataFrame, subtitles_dir: Path) -> tuple[list[Window], BuildStats]:
    stats = BuildStats()
    windows: list[Window] = []
    loaded_subtitles: dict[str, list[Cue]] = {}

    for _, row in df.iterrows():
        video_id = str(row["video_id"]).strip()
        segment_index = str(row["segment_index"]).strip()
        segment_start = parse_timestamp(row["segment_start"])
        segment_end = parse_timestamp(row["segment_end"])
        stats.segments += 1

        if video_id not in loaded_subtitles:
            try:
                path = find_subtitle_file(subtitles_dir, video_id)
                cues, subtitle_format = parse_subtitles(path)
            except Exception as exc:  # noqa: BLE001
                stats.file_errors.append(f"{video_id}: {exc}")
                loaded_subtitles[video_id] = []
                continue
            loaded_subtitles[video_id] = cues
            stats.formats[subtitle_format] = stats.formats.get(subtitle_format, 0) + 1

        cues = loaded_subtitles[video_id]
        if not cues:
            continue

        segment_windows, dropped = build_windows(
            cues, video_id, segment_index, segment_start, segment_end
        )
        if not segment_windows:
            stats.segments_too_short += 1
        stats.dropped_seconds += dropped
        stats.kept_seconds += len(segment_windows) * WINDOW_SECONDS
        windows.extend(segment_windows)

    for window in windows:
        if len(window.text) < MIN_CHARS:
            stats.empty_windows += 1

    return windows, stats


def print_stats(stats: BuildStats, windows: list[Window], split_name: str) -> None:
    total_seconds = stats.kept_seconds + stats.dropped_seconds
    print(f"split {split_name}: {stats.segments} segments -> {len(windows)} windows")
    print(f"  formats seen        : {stats.formats}")
    print(f"  segments < {WINDOW_SECONDS}s     : {stats.segments_too_short}")
    print(f"  seconds kept        : {stats.kept_seconds:.0f}")
    if total_seconds:
        pct = 100 * stats.dropped_seconds / total_seconds
        print(f"  seconds dropped     : {stats.dropped_seconds:.0f} ({pct:.1f}% of segment time)")
    else:
        print("  seconds dropped     : 0")
    print(f"  windows < {MIN_CHARS} chars : {stats.empty_windows} (labelled locally, no API call)")
    for err in stats.file_errors:
        print(f"  FILE ERROR: {err}", file=sys.stderr)
