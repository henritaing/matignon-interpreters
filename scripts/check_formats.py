'''Count videos grouped by codec, fps, and resolution.'''

import json
import subprocess
from collections import Counter
from pathlib import Path

VIDEOS_DIR = Path("data/videos")

counts = Counter()
for video_path in VIDEOS_DIR.glob("*.mp4"):
    # to run ffprobe and capture its output
    ffprobe_output = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json",
         "-show_streams", "-select_streams", "v:0", str(video_path)],
        capture_output=True, text=True, check=True,
    ).stdout
    video_stream = json.loads(ffprobe_output).get("streams", [{}])[0]

    frame_rate_numerator, frame_rate_denominator = video_stream.get("r_frame_rate", "0/1").split("/")
    fps = round(int(frame_rate_numerator) / int(frame_rate_denominator))

    codec = video_stream.get("codec_name", "?")
    resolution = f"{video_stream.get('width', '?')}x{video_stream.get('height', '?')}"
    counts[(codec, fps, resolution)] += 1

for (codec, fps, resolution), count in sorted(counts.items()):
    print(f"{codec} {fps}fps {resolution} : {count} videos")
