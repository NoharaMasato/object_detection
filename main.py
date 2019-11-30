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
from myobject import MyVideoNormal
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
        if myframe.key_frame or myvideoav.is_objects_overlaped(): #物体がかぶっている時ももう一度ssdにかける
            print("ssd" + str(cnt))
            myvideoav.reset_objects()
            pts, display_txts = ssd_model_opencv.detect_from_ssd(myframe.data,myframe.cnt)
            for pt, display_txt in zip(pts, display_txts):
                myobject = MyObject(pt,display_txt,(0,0,255))
                myvideoav.add_object(myobject)
        else:
            print("mv" + str(cnt))
            pts_tmp = ssd_model_opencv.detect_from_mv(myframe.data,myframe.cnt,myframe.mvs)
            for myobject in myvideoav.objects:
                if (len(pts_tmp) != 0):
                    next_pt = myvideoav.select_nearest_pt(pts_tmp,myobject)
                    myobject.move(next_pt) #objectを動かす
                    myobject.color = (255,0,0)

        # 動画を表示する(frameにobjectsも書き込んでくれる)
        myvideoav.forward_frame(save = 1,play = 1)

def detect_object_from_all_frame(file_path):
    myvideo = MyVideoNormal(file_path)
    cnt=0

    while(myvideo.cap.isOpened()):
        cnt+=1
        myframe = myvideo.read_frame(cnt)

        if cnt == 1:
            myvideo.init_meta_data(myframe.data)
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
    myvideo = MyVideoNormal(file_path)
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
    myvideo = MyVideoNormal(file_path)
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

