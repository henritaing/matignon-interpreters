from pytube import YouTube, Playlist
import cv2
import numpy as np
import re
from matplotlib import pyplot as plt
from IPython.display import clear_output
import os
from youtube_transcript_api.formatters import JSONFormatter
import tqdm
#import moviepy.editor as mpe
import pytube
from youtube_transcript_api import YouTubeTranscriptApi

root_path = "data/download_videos"
os.makedirs(root_path, exist_ok=True)
os.makedirs(root_path+'/video', exist_ok=True)
os.makedirs(root_path+'/cropped_videos', exist_ok=True)

p = Playlist("https://www.youtube.com/watch?v=0hXvxmgHk_c&list=PLgtU_g_Bn-2Y1tvjm97zGzEZDhnpiM6Au")
