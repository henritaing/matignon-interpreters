import cv2
import matplotlib.pyplot as plt
from IPython.display import clear_output
import os


def crop_video(filename, out_filename, x0, x1, y0, y1, visualize=False):

    cap = cv2.VideoCapture(filename)
    fps = cap.get(cv2.CAP_PROP_FPS)
    out = cv2.VideoWriter(out_filename, cv2.VideoWriter_fourcc(*'MP4V'), fps, (x1-x0, y1-y0))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    i = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if ret != True:
            break
        i += 1
        if visualize:
            if (i%16 == 0):
                clear_output(wait=True)
                plt.axis("off")
                plt.imshow(frame[:, :, ::-1])
                plt.show()
                plt.imshow(frame[y0:y1, x0:x1, ::-1])
                plt.show()
        out.write(frame[y0:y1, x0:x1])

    cap.release()
    out.release()
    return frame_count

root_path = "data"

for file in os.listdir(root_path+'/videos/'):
    outfilename = (root_path+'/cropped_videos/'+file).replace(".mp4", "_cropped.mp4")
    if os.path.exists(outfilename):
        print(f"Skipping {file}, already cropped")
        continue
    print(f"Cropping {file}...")
    crop_video(root_path+'/videos/'+file, outfilename, 1334, 1334+494, 417, 417+494, visualize=False)