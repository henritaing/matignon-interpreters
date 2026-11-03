'''Detect blank frames in a video using HSV color space to identify transitions.'''

import cv2
import numpy as np

SAT_MAX = 30
VAL_MIN = 200
SAMPLE_EVERY = 15             # ~2 fps at 30 fps source
ENTER_STDS_ABOVE_MEAN = 2.0   # how many std above mean to enter blank state
EXIT_STDS_ABOVE_MEAN = 0.5    # how many std above mean to exit blank state
MAX_GAP = 4.0                 # transitions don't last longer than 4 seconds


def blank_fraction(frame_bgr: np.ndarray) -> float:
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
    mask = (hsv[:, :, 1] <= SAT_MAX) & (hsv[:, :, 2] >= VAL_MIN)
    return float(mask.mean())


def find_transitions(filename: str) -> list[list[float]]:
    """Return a list of [start, end] pairs (in seconds) for each blank transition."""
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
        times.append(i / fps)
        fracs.append(blank_fraction(frame))
        i += SAMPLE_EVERY
        for _ in range(SAMPLE_EVERY - 1):
            cap.grab()
    cap.release()

    fracs_array = np.array(fracs)
    baseline_mean = fracs_array.mean()
    baseline_std = fracs_array.std()
    enter_threshold = baseline_mean + ENTER_STDS_ABOVE_MEAN * baseline_std
    exit_threshold = baseline_mean + EXIT_STDS_ABOVE_MEAN * baseline_std

    in_blank = False
    blank_timestamps = []
    for t, frac in zip(times, fracs):
        if not in_blank and frac > enter_threshold:
            in_blank = True
        elif in_blank and frac < exit_threshold:
            in_blank = False
        if in_blank:
            blank_timestamps.append(t)

    transitions = []
    if blank_timestamps:
        start = blank_timestamps[0]
        end = blank_timestamps[0]
        for t in blank_timestamps[1:]:
            if t - end > MAX_GAP:
                transitions.append([start, end + 0.5])
                start = t
            end = t
        transitions.append([start, end + 0.5])

    return transitions


if __name__ == "__main__":
    filename = r"data\cropped_videos\-sgE2QHsskA_clip_cropped.mp4"
    print(find_transitions(filename))
