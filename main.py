import time
import imutils
import cv2
from PIL import Image
import av
import os
import numpy as np
import matplotlib.pyplot as plt
import sys

sys.path.append('src')
sys.path.append('yolo')
import ssd_model_opencv
import yolo
import read_csv
from myobject import *
import consts


def detect_object_from_key_frame(filepath,mvs):
    myvideoav = MyVideoAV(filepath)
    cnt=0
    former_pts = []

    for idx, frame in enumerate(myvideoav.video.decode(video=0)):
        myframe = MyFrame(frame.to_ndarray(format='bgr24'), frame.key_frame, cnt, mvs[cnt])
        cnt+=1
        if cnt == 1:
            myvideoav.init_meta_data(myframe.data)

        myvideoav.frames.append(myframe)
        #ここで、key_frameとそれ以外に分けて、物体検知をしたポインタを返したい
        if myframe.key_frame or (consts.CONSIDER_OVERLAPPED and myvideoav.is_objects_overlaped()): #物体がかぶっている時ももう一度ssdにかける
            before_objects = myvideoav.reset_objects()

            if consts.SSD:
                pts, display_txts = ssd_model_opencv.detect_from_ssd(myframe.data,cnt)
            if consts.YOLO:
                pts, display_txts = yolo.detect_from_yolo(myframe.data,cnt)

            for pt, display_txt in zip(pts, display_txts):
                myobject = MyObject(pt,display_txt,(0,0,255))
                myvideoav.add_object(myobject)
        else:
            if consts.VECTOR_DIR:
                for myobject in myvideoav.objects:
                    vector = myobject.caliculate_vector(myframe.data,myframe.mvs)
                    next_pt = [myobject.pt[i] + vector[i%2]*10 for i in range(4)] #ある定数をかけて、動かす
                    myobject.move(next_pt) #objectを動かす
                    myobject.color = (255,0,0)
            else:
                pts_tmp = ssd_model_opencv.detect_from_mv(myframe.data,myframe.cnt,myframe.mvs)
                for myobject in myvideoav.objects:
                    if (len(pts_tmp) != 0):
                        next_pt = myvideoav.select_nearest_pt(pts_tmp,myobject)
                        myobject.move(next_pt) #objectを動かす
                        myobject.color = (255,0,0)

        # 動画を表示する(frameにobjectsも書き込んでくれる)
        myvideoav.forward_frame(save = consts.SAVE,play = consts.PLAY)

    if consts.ACCURACY:
        print("final_accuracy:" + str((sum(myvideoav.accuracies) / len(myvideoav.accuracies))*100) + "%")
        return sum(myvideoav.accuracies) / len(myvideoav.accuracies)

def change_detect_interval(filepath,mvs,interval):
    myvideoav = MyVideoAV(filepath)
    cnt=0
    former_pts = []
    for idx, frame in enumerate(myvideoav.video.decode(video=0)):
        cnt+=1
        myframe = MyFrame(frame.to_ndarray(format='bgr24'), frame.key_frame, cnt, mvs[cnt])

        if cnt == 1:
            myvideoav.init_meta_data(myframe.data)

        myvideoav.frames.append(myframe)
        #ここで、key_frameとそれ以外に分けて、物体検知をしたポインタを返したい
        if (cnt-1)%interval == 0:
            myvideoav.reset_objects()

            if consts.SSD:
                pts, display_txts = ssd_model_opencv.detect_from_ssd(myframe.data,cnt)
            if consts.YOLO:
                pts, display_txts = yolo.detect_from_yolo(myframe.data,cnt)

            for pt, display_txt in zip(pts, display_txts):
                myobject = MyObject(pt,display_txt,(0,0,255))
                myvideoav.add_object(myobject)
        else:
            if consts.VECTOR_DIR:
                for myobject in myvideoav.objects:
                    vector = myobject.caliculate_vector(myframe.data,myframe.mvs)
                    next_pt = [myobject.pt[i] + vector[i%2]*10 for i in range(4)] #ある定数をかけて、動かす
                    myobject.move(next_pt) #objectを動かす
                    myobject.color = (255,0,0)
            else:
                pts_tmp = ssd_model_opencv.detect_from_mv(myframe.data,myframe.cnt,myframe.mvs)
                for myobject in myvideoav.objects:
                    if (len(pts_tmp) != 0):
                        next_pt = myvideoav.select_nearest_pt(pts_tmp,myobject)
                        myobject.move(next_pt) #objectを動かす
                        myobject.color = (255,0,0)

        # 動画を表示する(frameにobjectsも書き込んでくれる)
        myvideoav.forward_frame(save = consts.SAVE,play = consts.PLAY)
    return sum(myvideoav.accuracies) / len(myvideoav.accuracies)

def detect_object_from_all_frame(file_path):
    myvideo = MyVideoNormal(file_path)
    cnt=0

    while(myvideo.cap.isOpened()):
        cnt+=1
        myframe = myvideo.read_frame(cnt)

        if cnt == 1:
            myvideo.init_meta_data(myframe.data)
        if myframe != 0:
            if consts.SSD:
                pts, display_txts = ssd_model_opencv.detect_from_ssd(myframe.data,cnt)
            if consts.YOLO:
                pts, display_txts = yolo.detect_from_yolo(myframe.data,cnt)
        else:
            break

        myvideo.reset_objects()
        for pt, display_txt in zip(pts, display_txts):
            myobject = MyObject(pt,display_txt,(0,0,255))
            myvideo.add_object(myobject)

        myvideo.frames.append(myframe)
        myvideo.forward_frame(save = consts.SAVE,play = consts.PLAY)

    myvideo.finish_play()
    if consts.ACCURACY:
        print("final_accuracy:" + str((sum(myvideo.accuracies) / len(myvideo.accuracies))*100) + "%")

def detect_only_i(filepath):
    myvideoav = MyVideoAV(filepath)
    cnt=0
    for idx, frame in enumerate(myvideoav.video.decode(video=0)):
        cnt+=1
        myframe = MyFrame(frame.to_ndarray(format='bgr24'), frame.key_frame, cnt)

        if cnt == 1:
            myvideoav.init_meta_data(myframe.data)

        myvideoav.frames.append(myframe)

        if myframe.key_frame: 
            myvideoav.reset_objects()

            if consts.SSD:
                pts, display_txts = ssd_model_opencv.detect_from_ssd(myframe.data,cnt)
            if consts.YOLO:
                pts, display_txts = yolo.detect_from_yolo(myframe.data,cnt)

            for pt, display_txt in zip(pts, display_txts):
                myobject = MyObject(pt,display_txt,(0,0,255))
                myvideoav.add_object(myobject)
        myvideoav.forward_frame(save = consts.SAVE,play = consts.PLAY)

def show_motion_vector(file_path,mvs):
    myvideo = MyVideoNormal(file_path)
    cnt=0

    while(myvideo.cap.isOpened()):
        myframe = myvideo.read_frame(cnt,mvs[cnt])
        cnt+=1
        if cnt == 1:
            myvideo.init_meta_data(myframe.data)
        if myframe == 0:
            break
        myframe.embed_mv()
        if consts.SAVE:
            myframe.save_frame(myvideo)
        myframe.display_frame()

    myvideo.finish_play()

def just_play(file_path):
    myvideo = MyVideoNormal(file_path)
    cnt=0

    while(myvideo.cap.isOpened()):
        cnt+=1
        myframe = myvideo.read_frame(cnt)
        if myframe == 0:
            break
        myframe.display_frame()

    myvideo.finish_play()

if __name__ == '__main__':
    args = sys.argv
    start = time.time()

    if len(args) != 2:
        print("引数にi or all or show_mv or play を入れてください")
        exit(1)
    file_path = "sample_videos/" +  consts.FILE_NAME + ".mp4"

    if args[1] == "all":
        detect_object_from_all_frame(file_path)
    elif args[1] == "play":
        just_play(file_path)
    elif args[1] == "di": # detect only i
        detect_only_i(file_path)
    else: #動きベクトルを使う方
        csv_file_name = "mv_csv/" + consts.FILE_NAME + ".csv"
        mvs = read_csv.read_filtered_mv_from_csv(csv_file_name)

        if args[1] == "i":
            detect_object_from_key_frame(file_path,mvs)
        elif args[1] == "show_mv":
            show_motion_vector(file_path,mvs)
        elif args[1] == "inter":
            elapsed_times = []
            accuracies = []
            for i in consts.I_INTER_VALS:
                start_inter = time.time()
                accuracies.append(change_detect_interval(file_path,mvs,i))
                elapsed_time = time.time() - start_inter
                elapsed_times.append(elapsed_time)
                print ("かかった時間:{0}".format(elapsed_time) + "[sec]:"+ str(i) + "枚ごとに検出,最終的な精度:" + str(accuracies[-1]) + "%")

            for x,y,k in zip(elapsed_times,accuracies,consts.I_INTER_VALS):
                plt.plot(x,y,'o')
                #plt.annotate(round(300/k,1), xy=(x,y)) #plotにラベル付けをするかどうか

            start_inter = time.time()
            y = detect_object_from_key_frame(file_path,mvs) #Iフレームのみの回
            x = time.time() - start_inter
            plt.plot(x,y,'o')
            plt.annotate("I", xy=(x,y))

            plt.xlabel('time [s]')
            plt.ylabel('accuracy [%]')
            plt.show()
        else:
            print("引数にi or all or show_mv or play を入れてください")
            exit(1)

    elapsed_time = time.time() - start
    print ("かかった合計時間:{0}".format(elapsed_time) + "[sec]")

