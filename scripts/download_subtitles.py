'''Download text subtitles with timestamps from a YouTube playlist using yt-dlp.'''

import os
import yt_dlp

PLAYLIST_URL = "https://www.youtube.com/watch?v=0hXvxmgHk_c&list=PLgtU_g_Bn-2Y1tvjm97zGzEZDhnpiM6Au"
OUTPUT_DIR = "data/subtitles"

os.makedirs(OUTPUT_DIR, exist_ok=True)

ydl_opts = {
    "skip_download": True,
    "writesubtitles": True,
    "writeautomaticsub": True,
    "subtitleslangs": ["fr"],
    "subtitlesformat": "srt",
    "outtmpl": f"{OUTPUT_DIR}/%(id)s_clip_subtitles.%(ext)s",
    "ignoreerrors": True,
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([PLAYLIST_URL])
