import cv2
import os
import time

# 视频转为图片
def video2imgs(input_filepath, interval=1):
    now_timestamp = str(int(time.time()))
    cap = cv2.VideoCapture(input_filepath)
    fps = cap.get(cv2.CAP_PROP_FPS)
    interval = fps/10
    # frame = cap.get(cv2.CAP_PROP_FRAME_COUNT)

    i, j = 0, 0
    while cap.isOpened():
        i += 1
        ret, frame = cap.read()
        if i % interval == 0:
            j += 1
            print("j = ", j)
            if ret:
                output_dir = os.path.join(os.path.dirname(os.path.abspath(input_filepath)), "output_"+now_timestamp)
                if not os.path.exists(output_dir):
                    os.mkdir(output_dir)
                output_filepath = str(j) + ".jpg"
                print(os.path.join(output_dir, output_filepath))
                flag = cv2.imwrite(os.path.join(output_dir, output_filepath), frame)
            else:
                break
        if j > 2000:
            break
    cap.release()

# 获取视频帧速率和总帧数
def get_fps_and_frame(file):
    videoCapture = cv2.VideoCapture(file)
    fps = videoCapture.get(cv2.CAP_PROP_FPS)
    frame = videoCapture.get(cv2.CAP_PROP_FRAME_COUNT)
    return fps, frame

if __name__ == "__main__":
    filename = "D:/Program Files (x86)/威猛的坤舞.mov"
    video2imgs(filename)
