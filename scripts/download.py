import os
import yt_dlp

PLAYLIST_URL = "https://www.youtube.com/watch?v=0hXvxmgHk_c&list=PLgtU_g_Bn-2Y1tvjm97zGzEZDhnpiM6Au"
OUTPUT_DIR = "data/download_videos/videos"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs("data/download_videos/cropped_videos", exist_ok=True)

ydl_opts = {
    "format": "bestvideo[ext=mp4][height=1080]/best[ext=mp4]/best",
    "outtmpl": f"{OUTPUT_DIR}/%(id)s_clip.%(ext)s",
    "ignoreerrors": True,
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([PLAYLIST_URL])

