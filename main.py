import time
import imutils
import cv2
from PIL import Image
import av
import os
import numpy as np
import sys

sys.path.append('src')
sys.path.append('yolo')
import ssd_model_opencv
import yolo
import read_csv
from myobject import *
import consts

def detect_object_from_key_frame(filepath,mvs,interval=0,use_mvs = 0):
    myvideoav = MyVideoAV(filepath)
    cnt=0
    if consts.ACCURACY:
        start_inter = time.time()

    for idx, frame in enumerate(myvideoav.video.decode(video=0)):
        myframe = MyFrame(frame.to_ndarray(format='bgr24'), frame.key_frame, cnt, mvs[cnt])
        if cnt == 0:
            myvideoav.init_meta_data(myframe.data)

        myvideoav.frames.append(myframe)
        #ここで、key_frameとそれ以外に分けて、物体検知をしたポインタを返したい
        if  myframe.key_frame or (interval != 0 and cnt % interval == 0) or (consts.CONSIDER_OVERLAPPED and myvideoav.is_objects_overlaped()): #物体がかぶっている時ももう一度ssdにかける

            if consts.SSD:
                pts, display_txts = ssd_model_opencv.detect_from_ssd(myframe.data)
            if consts.YOLO:
                pts, display_txts = yolo.detect_from_yolo(myframe.data,cnt)

            if pts != []:
                before_objects = myvideoav.reset_objects()

            for pt, display_txt in zip(pts, display_txts):
                myobject = MyObject(pt,display_txt,(0,0,255))
                myvideoav.add_object(myobject)
        elif use_mvs:
            if consts.VECTOR_DIR:
                for myobject in myvideoav.objects:
                    vector = myobject.caliculate_vector(myframe.data,myframe.mvs)
                    next_pt = [myobject.pt[i] + vector[i%2]*1.5 for i in range(4)] #ある定数をかけて、動かす
                    myobject.move(next_pt) #objectを動かす
                    myobject.color = (255,0,0)
            else:
                pts_tmp = ssd_model_opencv.detect_from_mv(myframe.data,myframe.mvs)
                for myobject in myvideoav.objects:
                    if len(pts_tmp) != 0:
                        next_pt = myvideoav.select_nearest_pt(pts_tmp,myobject.pt)
                        myobject.move(next_pt) #objectを動かす
                        myobject.color = (255,0,0)
        # 動画を表示する(frameにobjectsも書き込んでくれる)
        cnt+=1
        myvideoav.forward_frame(save = consts.SAVE,play = consts.PLAY)

    if consts.ACCURACY:
        elapsed_time = time.time() - start_inter
        accuracy = sum(myvideoav.accuracies) / len(myvideoav.accuracies)
        print ("かかった時間(動きベクトル):{0}".format(elapsed_time) + "[sec]:"+ str(interval) + "枚ごとに検出,最終的な精度:" + str(accuracy*100) + "%")
        return accuracy,elapsed_time

def detect_only_i(filepath):
    myvideoav = MyVideoAV(filepath)
    cnt=0
    for idx, frame in enumerate(myvideoav.video.decode(video=0)):
        myframe = MyFrame(frame.to_ndarray(format='bgr24'), frame.key_frame, cnt)

        if cnt == 0:
            myvideoav.init_meta_data(myframe.data)

        myvideoav.frames.append(myframe)

        if myframe.key_frame: 
            myvideoav.reset_objects()

            if consts.SSD:
                pts, display_txts = ssd_model_opencv.detect_from_ssd(myframe.data)
            if consts.YOLO:
                pts, display_txts = yolo.detect_from_yolo(myframe.data,cnt)

            for pt, display_txt in zip(pts, display_txts):
                myobject = MyObject(pt,display_txt,(0,0,255))
                myvideoav.add_object(myobject)
        myvideoav.forward_frame(save = consts.SAVE,play = consts.PLAY)
        cnt+=1

def show_motion_vector(file_path,mvs):
    myvideo = MyVideoNormal(file_path)
    cnt=0

    while(myvideo.cap.isOpened()):
        myframe = myvideo.read_frame(cnt,mvs[cnt])
        if cnt == 0:
            myvideo.init_meta_data(myframe.data)
        if myframe == 0:
            break
        myframe.embed_mv()
        if consts.SAVE:
            myframe.save_frame(myvideo)
        myframe.display_frame()
        cnt+=1

    myvideo.finish_play()

def just_play(file_path):
    myvideo = MyVideoNormal(file_path)
    cnt=0

    while(myvideo.cap.isOpened()):
        myframe = myvideo.read_frame(cnt)
        if myframe == 0:
            break
        myframe.display_frame()
        cnt+=1

    myvideo.finish_play()

if __name__ == '__main__':
    args = sys.argv
    start = time.time()

    if len(args) != 2:
        print("引数にi or all or show_mv or play を入れてください")
        if (args[1] == 'i' or args[1] == 'all') and len(args) == 3:
            interval = int(args[2])
        else:
            exit(1)
    elif args[1] == 'i':
        interval = 0
    elif args[1] == 'all':
        interval = 1

    if consts.OBT:
        file_path = "obt/"+consts.FILE_NAME + ".mp4"
    else:
        file_path = "sample_videos/" +  consts.FILE_NAME + ".mp4"

    if args[1] == "play":
        just_play(file_path)
    elif args[1] == "di": # detect only i
        detect_only_i(file_path)
    else: #動きベクトルを使う方
        csv_file_name = "mv_csv/" + consts.FILE_NAME + ".csv"
        mvs = read_csv.read_filtered_mv_from_csv(csv_file_name)

        if args[1] == "i":
            detect_object_from_key_frame(file_path,mvs,interval,use_mvs = 1)
        elif args[1] == "all":
            detect_object_from_key_frame(file_path,mvs,interval,use_mvs = 0)
        elif args[1] == "show_mv":
            show_motion_vector(file_path,mvs)
        elif args[1] == "inter":
            elapsed_times = []
            accuracies = []
            for i in consts.I_INTER_VALS:
                accuracy_val,elapsed_time = detect_object_from_key_frame(file_path,mvs,i,use_mvs = 1) #動きベクトルを使う
                accuracies.append([accuracy_val,0])
                elapsed_times.append(elapsed_time)

                accuracy_val,elapsed_time = detect_object_from_key_frame(file_path,mvs,i,use_mvs = 0) #ただ間引くだけ
                accuracies.append([accuracy_val,1])
                elapsed_times.append(elapsed_time)

            accuracy.show_graph(elapsed_times,accuracies)

        else:
            print("引数にi or all or show_mv or play を入れてください")
            exit(1)

    elapsed_time = time.time() - start
    print ("かかった合計時間:{0}".format(elapsed_time) + "[sec]")

