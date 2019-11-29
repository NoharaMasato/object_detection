import time
import imutils
import cv2
from PIL import Image
import ssd_model_opencv
import read_csv
import av
import numpy as np
import sys

fourcc = cv2.VideoWriter_fourcc(*'MPEG')
out = cv2.VideoWriter('output_videos/output.mp4',fourcc, 20.0, (1280,720)) #画像のサイズが違うと、保存した時に再生に失敗する

def detect_object_from_key_frame(filepath,mvs):
    video_container = av.open(filepath)
    cnt=0

    pts = []
    former_pts = []
    display_txts = []
    box_color = (0,255,0)
    for idx, frame in enumerate(video_container.decode(video=0)):
        cnt+=1
        is_key_frame = frame.key_frame
        frame = frame.to_ndarray(format='bgr24')

        #ここで、key_frameとそれ以外に分けて、物体検知をしたポインタを返したい
        pts_tmp = []
        if is_key_frame:
            pts, display_txts = ssd_model_opencv.detect_from_ssd(frame,cnt)
            box_color = (0,0,255)
        else:
            pts_tmp = ssd_model_opencv.detect_from_mv(frame,cnt,mvs[cnt])
            # フレームにある一定の大きさ以上の動きベクトルの塊があった場合にのみ置き換える。その他場合は以前のフレームのものをそのまま使う
            pts_tmp2 = []
            for pt_tmp in pts_tmp:
                flag = False
                for former_pt in former_pts:
                    threash = 10
                    if pt_tmp[2] < former_pt[0]-threash or pt_tmp[0]-threash > former_pt[2] or pt_tmp[1]-threash > former_pt[3] or pt_tmp[3]-threash < former_pt[1]:
                        1 + 1
                    else:
                        flag = True
                if flag == True:
                    pts_tmp2.append(pt_tmp)

            if len(pts_tmp2) >= 1:
                pts = pts_tmp2
                box_color = (0,255,0)

        for pt, display_txt in zip(pts, display_txts):
            cv2.rectangle(frame, (pt[0], pt[1]), (pt[2], pt[3]), color=box_color, thickness=2)
            cv2.putText(frame, display_txt,(pt[0],pt[1]),cv2.FONT_HERSHEY_SIMPLEX,1,box_color,2,cv2.LINE_AA)

        former_pts = pts

        #動画を保存する
        out.write(frame)

        # 画質が良すぎると、oepncvは描写するのにかなり時間がかかってしまうため、画質を悪くする
        # frame rateを測る時は、画面を描写せずにやると、時間が早くなりそう
        frame = imutils.resize(frame, width=450)

        cv2.imshow("Test", frame)

        cv2.waitKey(1)

def detect_object_from_all_frame(file_path):
    cap = cv2.VideoCapture(file_path)
    cnt=0

    pts = []
    display_txts = []
    while(cap.isOpened()):
        cnt+=1
        print(str(cnt) + "\n")
        ret, frame = cap.read()
        if ret:
            pts, display_txts = ssd_model_opencv.detect_from_ssd(frame,cnt)
        else:
            break
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        for pt, display_txt in zip(pts, display_txts):
            cv2.rectangle(frame, (pt[0], pt[1]), (pt[2], pt[3]), color=(0, 255, 0), thickness=2) 
            cv2.putText(frame, display_txt,(pt[0],pt[1]),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2,cv2.LINE_AA)

        out.write(frame)
        frame = imutils.resize(frame, width=450)
        cv2.imshow('frame',frame)
        cv2.waitKey(1)

    cap.release()
    cv2.destroyAllWindows() 

def show_motion_vector(file_path,mvs):
    cap = cv2.VideoCapture(file_path)
    cnt=0

    while(cap.isOpened()):
        cnt+=1

        ret, frame = cap.read()

        if ret == 0:
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        for nowy in range(read_csv.frame_height):
            for nowx in range(read_csv.frame_width):
                mv = mvs[cnt][nowy][nowx]
                if (mv > 0):
                    cv2.rectangle(frame, (nowx*8, nowy*8), ((nowx+1)*8, (nowy+1)*8), color=(255, 0, 0), thickness=-1) # thickness = -1は塗りつぶす

        out.write(frame)
        frame = imutils.resize(frame, width=450)
        cv2.imshow('frame',frame)

        cv2.waitKey(1)

    cap.release()
    cv2.destroyAllWindows() 

def just_play(file_path):
    cap = cv2.VideoCapture(file_path)
    while(cap.isOpened()):
        ret, frame = cap.read()
        frame = imutils.resize(frame, width=450)
        cv2.imshow('frame',frame)
        cv2.waitKey(1)

if __name__ == '__main__':
    args = sys.argv
    start = time.time()

    if len(args) != 2:
        print("引数にi or all or show_mv or play を入れてください")
        exit(1)

    file_name = "dog_out"
    file_path = "sample_videos/" + file_name + ".mp4"
    csv_file_name = "mv_csv/" + file_name + ".csv"
    read_csv.numpy_array_file_name += (file_name + ".npy")
    mvs = read_csv.read_csv(csv_file_name)

    if args[1] == "all":
        detect_object_from_all_frame(file_path)
    elif args[1] == "i":
        detect_object_from_key_frame(file_path,mvs)
    elif args[1] == "show_mv":
        show_motion_vector(file_path,mvs)
    elif args[1] == "play":
        just_play(file_path)

    elapsed_time = time.time() - start
    print ("かかった時間:{0}".format(elapsed_time) + "[sec]")

