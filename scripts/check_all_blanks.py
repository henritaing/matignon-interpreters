'''Run blank transition detection on all cropped videos and print results.'''

from pathlib import Path

from blank import find_transitions

VIDEOS_DIR = Path("data/cropped_videos")

number_of_transitions = 0

videos = {}

for video_path in sorted(VIDEOS_DIR.glob("*.mp4")):
    transitions = find_transitions(str(video_path))
    videos[video_path.name] = len(transitions)
    print(f"{video_path.name}: {transitions}")
    number_of_transitions += len(transitions)

print(f"Total number of transitions: {number_of_transitions}")
print(videos)