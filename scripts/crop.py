import cv2
import matplotlib.pyplot as plt
from IPython.display import clear_output

def crop_video(filename, out_filename, fps, x0, x1, y0, y1, visualize=False):

    cap = cv2.VideoCapture(filename)
    out = cv2.VideoWriter(out_filename, cv2.VideoWriter_fourcc(*'MP4V'), fps, (x1-x0, y1-y0))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    i =0
    while cap.isOpened():
        ret, frame = cap.read()
        if ret != True:
            break
        i+=1
        if visualize:
            if (i%16 == 0):
                clear_output(wait=True)
                plt.axis("off")
                plt.imshow(frame[:, :, ::-1])
                plt.show()
                plt.imshow(frame[y0:y1, x0:x1, ::-1])
                plt.show()
        out.write(frame[y0:y1, x0:x1])
        
    out.release()
    return frame_count