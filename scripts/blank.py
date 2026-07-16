'''Detect blank frames in a video using HSV color space to identify transitions.'''

import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import argrelmax

def blank_fraction(frame_bgr: np.ndarray, SAT_MAX: int, VAL_MIN: int) -> float:
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV) # use saturation and value to detect blank frames, as they are usually white or gray
    mask = (hsv[:, :, 1] <= SAT_MAX) & (hsv[:, :, 2] >= VAL_MIN) # 1 is saturation, 2 is value
    return float(mask.mean())

filename = r"data\cropped_videos\-sgE2QHsskA_clip_cropped.mp4"
SAT_MAX, VAL_MIN = 30, 200
SAMPLE_EVERY = 15  # ~2 fps at 30 fps source

cap = cv2.VideoCapture(filename)
if not cap.isOpened():                     
    raise RuntimeError(f"could not open {filename}")
fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

times, fracs = [], []
first_frame = ((9000 // SAMPLE_EVERY) + 1) * SAMPLE_EVERY
cap.set(cv2.CAP_PROP_POS_FRAMES, first_frame) # first 5 minutes are intro and not relevant for blank detection
i = first_frame
while True:
    ret, frame = cap.read()
    if not ret:
        break
    times.append(i / fps)
    fracs.append(blank_fraction(frame, SAT_MAX, VAL_MIN))
    i += SAMPLE_EVERY
    for _ in range(SAMPLE_EVERY - 1):
        cap.grab()  # advance without decoding; outer read() catches EOF
cap.release()

fracs = np.array(fracs)
times = np.array(times)

threshold = 0.6
MAX_GAP = 4.0 # transitions don't last longer than 4 seconds, so we can merge close timestamps as they would belong to the same transition

timestamps = times[fracs > threshold].tolist()

transitions = []
if timestamps:
    start = timestamps[0]
    end = timestamps[0]
    for t in timestamps[1:]:
        if t - end > MAX_GAP:
            transitions.append([start, end + 0.5])
            start = t
        end = t
    transitions.append([start, end + 0.5])

print(transitions)

# To adjust threshold for blank detection
# plt.figure(figsize=(14, 3))
# plt.plot(times, fracs, lw=0.8)
# for t in (0.7, 0.8, 0.9):
#     plt.axhline(t, ls="--", lw=0.6, color="r")
# plt.xlabel("time (s)"); plt.ylabel("blank fraction"); plt.ylim(0, 1)
# plt.title(f"sat_max={SAT_MAX} val_min={VAL_MIN}")
# plt.tight_layout(); plt.savefig("blankness2.png", dpi=110)