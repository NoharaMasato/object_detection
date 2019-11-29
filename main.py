import time
import imutils
import cv2
from PIL import Image
import ssd_model_opencv
import read_csv
import av
import numpy as np
import sys
from myobject import MyFrame
from myobject import MyObject
from myobject import MyVideo
from myobject import MyVideoAV


def detect_object_from_key_frame(filepath,mvs):
    myvideoav = MyVideoAV(filepath)

    cnt=0

    former_pts = []
    for idx, frame in enumerate(myvideoav.video.decode(video=0)):
        cnt+=1
        is_key_frame = frame.key_frame
        frame = frame.to_ndarray(format='bgr24')
          
        myframe = MyFrame(frame,is_key_frame,cnt,mvs[cnt])

        if cnt == 1:
            myvideoav.init_meta_data(myframe.data)

        myvideoav.frames.append(myframe)

        #ここで、key_frameとそれ以外に分けて、物体検知をしたポインタを返したい
        if myframe.key_frame:
            myvideoav.reset_objects()
            pts, display_txts = ssd_model_opencv.detect_from_ssd(myframe.data,myframe.cnt)
            for pt, display_txt in zip(pts, display_txts):
                myobject = MyObject(pt,display_txt,(255,0,0))
                myvideoav.add_object(myobject)
        #else:
            #pts_tmp = ssd_model_opencv.detect_from_mv(myframe.data,myframe.cnt,myframe.mvs)
            ## フレームにある一定の大きさ以上の動きベクトルの塊があった場合にのみ置き換える。その他場合は以前のフレームのものをそのまま使う
            #pts_tmp2 = []
            #for pt_tmp in pts_tmp:
            #    flag = False
            #    for former_pt in former_pts:
            #        threash = 10
            #        if pt_tmp[2] < former_pt[0]-threash or pt_tmp[0]-threash > former_pt[2] or pt_tmp[1]-threash > former_pt[3] or pt_tmp[3]-threash < former_pt[1]:
            #            1 + 1
            #        else:
            #            flag = True
            #    if flag == True:
            #        pts_tmp2.append(pt_tmp)

            #if len(pts_tmp2) >= 1:
            #    pts = pts_tmp2
            #    box_color = (0,255,0)

        #for pt, display_txt in zip(pts, display_txts):
        #    cv2.rectangle(frame, (pt[0], pt[1]), (pt[2], pt[3]), color=box_color, thickness=2)
        #    cv2.putText(frame, display_txt,(pt[0],pt[1]),cv2.FONT_HERSHEY_SIMPLEX,1,box_color,2,cv2.LINE_AA)

        #former_pts = pts

        # 動画を表示する
        myvideoav.forward_frame(save = 1)

def detect_object_from_all_frame(file_path):
    myvideo = MyVideo(file_path)
    cnt=0

    while(myvideo.cap.isOpened()):
        cnt+=1
        myframe = myvideo.read_frame(cnt)

        if cnt == 1:
            myvideo.set_width_and_height(myframe.data)
        if myframe != 0:
           pts, display_txts = ssd_model_opencv.detect_from_ssd(myframe.data,cnt)
        else:
            break

        myvideo.reset_objects()
        for pt, display_txt in zip(pts, display_txts):
            myobject = MyObject(pt,display_txt,(255,0,0))
            myvideo.add_object(myobject)

        myvideo.frames.append(myframe)
        myvideo.forward_frame(save = 1)

    myvideo.finish_play()

def show_motion_vector(file_path,mvs):
    myvideo = MyVideo(file_path)
    cnt=0

    while(myvideo.cap.isOpened()):
        cnt+=1

        myframe = myvideo.read_frame(cnt,mvs[cnt])
        if cnt == 1:
            myvideo.init_meta_data(myframe.data)
        if myframe == 0:
            break
        myframe.save_frame(myvideo)
        myframe.embed_mv()
        myframe.display_frame()

    myvideo.finish_play()

def just_play(file_path):
    myvideo = MyVideo(file_path)
    cnt=0

    while(myvideo.cap.isOpened()):
        cnt+=1
        myframe = myvideo.read_frame(cnt,mvs[cnt])
        if cnt == 1:
            myvideo.set_width_and_height(myframe.data)
        if myframe == 0:
            break
        myframe.save_frame(myvideo)
        myframe.display_frame()

    myvideo.finish_play()

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

