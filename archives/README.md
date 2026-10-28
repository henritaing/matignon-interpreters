# Matignon-LSF window classification

## Pipeline overview

```
split CSV
    └─▶  windowing.py        reads subtitle files, slices each segment into 2-min windows
              └─▶  claude_api.py   classifies each window with Claude, caches results
                       └─▶  classifywindows.py   writes out/<split>_windows.csv
```

## Files

| File | Role |
|---|---|
| `classifywindows.py` | Entry point — argparse, orchestration |
| `claude_api.py` | Claude API calls, result cache, CSV output |
| `windowing.py` | Window slicing, stats reporting |
| `subtitles.py` | SRT and transcript-format subtitle parsing |
| `timestamps.py` | Timestamp parsing and formatting |
| `config.py` | Shared constants (themes, thresholds, retries) |
| `prompt_theme_v1.txt` | System prompt sent to Claude; hashed and logged per run |

## Install

```
pip install anthropic pandas python-dotenv
```

Add your API key to `.env` at the project root:

```
ANTHROPIC_API_KEY=sk-ant-...
```

## Run

```bash
# 1. Always dry-run first: no API calls, reports coverage and token estimate.
python classifywindows.py --split-csv data/splits/splitA.csv --split-name A --dry-run

# 2. Real run.
python classifywindows.py --split-csv data/splits/splitA.csv --split-name A
```

Run from the `scripts/` directory. Outputs:
- `out/A_windows.csv` — one row per window with label and metadata
- `out/A_cache.jsonl` — raw API responses, used to resume interrupted runs

### All options

| Flag | Default | Description |
|---|---|---|
| `--split-csv` | *(required)* | Path to the split CSV |
| `--split-name` | *(required)* | Label used in output filenames |
| `--subtitles-dir` | `data/subtitles` | Directory containing subtitle files |
| `--prompt` | `prompt_theme_v1.txt` | System prompt file |
| `--out-dir` | `out` | Output directory |
| `--model` | `claude-sonnet-4-6` | Claude model to use |
| `--workers` | `4` | Parallel API threads |
| `--dry-run` | off | Report stats and cost estimate, no API calls |

## Expected data layout

```
data/
  subtitles/<VIDEO_ID>_clip_subtitles.fr    (or .srt variants)
  splits/<split>.csv                        columns: Video_ID, Segment_Index, Segment_Start, Segment_End
```

## Behaviour worth knowing

- **Tail dropped.** Each segment is cut into `floor(duration / 120)` windows; the remainder is discarded. Segments under 2 minutes yield zero windows. The dry-run prints how many seconds this costs.
- **Cue assignment.** A cue belongs to the window containing its *start* time. No text is duplicated across windows; boundary-spanning cues are not split.
- **Transcript format has no end times.** Cue end = next cue start; the last cue gets 5 seconds. This only affects cue durations, never window bounds.
- **Short windows skip the API.** Windows under `MIN_CHARS` (120 characters) are labelled `indéterminé` locally. Silence and applause windows cost nothing.
- **Resumable.** Results append to `out/<split>_cache.jsonl`, keyed by `(window_id, prompt_hash, model)`. Re-running skips already-cached windows. Editing the prompt changes its hash and invalidates the cache by design.
- **Failed calls are not cached** and will be retried on the next run.

## Self-consistency check (second pass)

```bash
cp out/A_cache.jsonl out/A_cache.pass1.jsonl
rm out/A_cache.jsonl
python classifywindows.py --split-csv data/splits/splitA.csv --split-name A
# compare label columns of the two runs; target agreement > 0.90
```
