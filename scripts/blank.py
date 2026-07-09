'''Detect blank frames in a video using HSV color space.'''

import cv2
import numpy as np
import matplotlib.pyplot as plt

def blank_fraction(frame_bgr: np.ndarray, SAT_MAX: int, VAL_MIN: int) -> float:
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV) # use saturation and value to detect blank frames, as they are usually white or gray
    mask = (hsv[:, :, 1] <= SAT_MAX) & (hsv[:, :, 2] >= VAL_MIN) # 1 is saturation, 2 is value
    return float(mask.mean())

filename = r"data\cropped_videos\_Lx00No3bZc_clip_cropped.mp4"
SAT_MAX, VAL_MIN = 30, 200
SAMPLE_EVERY = 15  # ~2 fps at 30 fps source

cap = cv2.VideoCapture(filename)
if not cap.isOpened():                     
    raise RuntimeError(f"could not open {filename}")
fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

times, fracs = [], []
i = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break
    if i % SAMPLE_EVERY == 0:
        times.append(i / fps)
        fracs.append(blank_fraction(frame, SAT_MAX, VAL_MIN))
    i += 1
cap.release()

fracs = np.array(fracs)
print(f"scored {len(fracs)} frames | median {np.median(fracs):.3f} | "
      f"p90 {np.percentile(fracs, 90):.3f} | p99 {np.percentile(fracs, 99):.3f} | "
      f"max {fracs.max():.3f} | ")

plt.figure(figsize=(14, 3))
plt.plot(times, fracs, lw=0.8)
for t in (0.7, 0.8, 0.9):
    plt.axhline(t, ls="--", lw=0.6, color="r")
plt.xlabel("time (s)"); plt.ylabel("blank fraction"); plt.ylim(0, 1)
plt.title(f"sat_max={SAT_MAX} val_min={VAL_MIN}")
plt.tight_layout(); plt.savefig("blankness.png", dpi=110)