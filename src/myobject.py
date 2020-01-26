import imutils
import cv2
import av
import numpy as np
import consts
import xml.etree.ElementTree as ET
import accuracy

class MyVideo:
    def __init__(self):
        self.frames = []
        self.objects = []
        self.gts = []

    def reset_objects(self):
        before_objects = self.objects
        self.objects = []
        return before_objects
    
    def read_frame(self,cnt,mvs = []):
        ret,frame = self.cap.read()
        if ret == 0:
            return 0
        else:
            myframe = MyFrame(frame,0,cnt,mvs)
            return myframe

    def init_meta_data(self,data):
        self.width = len(data[0])
        self.height = len(data)
        fourcc = cv2.VideoWriter_fourcc(*'MPEG')
        if consts.OBT:
            gts = [i.split(',') for i in open("obt_gt/" + consts.FILE_NAME + "_gt.txt", "r").read().split('\n')]
            self.gts = accuracy.parse_obt_gts(gts)
            myobject = MyObject(self.gts[0],'',(0,0,255))
            self.add_object(myobject)
        if consts.SAVE:
            self.out = cv2.VideoWriter('output_videos/output.mp4',fourcc, 20.0, (self.width,self.height))
        self.accuracies = []

    def finish_play(self):
        self.cap.release
        cv2.destroyAllWindows() 

    def add_object(self,my_object):
        self.objects.append(my_object)

    def forward_frame(self,save = 0,play = 1):
        myframe = self.frames[-1]
        myframe.embed_object_to_frame(self.objects)
        if consts.OBT and consts.SHOW_OBT_GT:
            myframe.embed_gt_to_frame(self.gts[myframe.cnt])

        if save != 0:
            myframe.save_frame(self)
        if play != 0:
            myframe.display_frame()
        if consts.ACCURACY == 1:
            self.calculate_accuracy(myframe.cnt)
            if consts.ACCURACY_PRINT == 1:
                print("accuracy:" + str(int((sum(self.accuracies) / len(self.accuracies))*100)) + "%,IoU:"+str(self.accuracies[-1]))

    def calculate_accuracy(self,frame_cnt): #frame_cntは0-indexed
        if consts.OBT:
            if self.objects != []:
                target_object_pt = self.objects[0].pt
            else:
                target_object_pt = [0,0,0,0]
            IoU = accuracy.bb_iou(target_object_pt, self.gts[frame_cnt])
        else:
            xml_file = "gt/"+consts.FILE_NAME+"/image_" + str(frame_cnt+1).zfill(3) + ".xml" #xmlファイルの番号は1-indexed
            xml_data = open(xml_file, "r").read()
            root = ET.fromstring(xml_data)
            for i in range(6,len(root)):
                pt = [0,0,0,0]
                if len(self.objects) > 0:
                    pt = self.objects[-1].pt
                pts = [myobject.pt for myobject in self.objects]
                ground_truth = [int(root[i][4][j].text) for j in range(4)]
                IoU = accuracy.calculate_biggest_iou(pts,ground_truth) #ground_truthと一番近いbbのIoUを返す
        if consts.USE_mAP50:
            if IoU >= 0.5:
                self.accuracies.append(1)
            else:
                self.accuracies.append(0)
        else:
            self.accuracies.append(IoU)


    def is_objects_overlaped(self):
        myobjects = self.objects
        for i in range(len(myobjects)):
            for j in range(i+1,len(myobjects)):
                # i番目のmyobjectとj番目のobjectとかぶっていないかをチェックする
                if myobjects[i].object_distance(myobjects[j]) < 200:
                    return True
        return False

    # object_ptに最も近いptを候補のptsから選び、戻り値として返す
    def select_nearest_pt(self,pts,object_pt):
        # ptsの中からbefore_ptに一番近いものを選ぶ
        nearest_pt = []
        biggest_iou = 0.0 #これより小さいiouのbbは無視する
        for pt in pts:
            iou = accuracy.bb_iou(object_pt,pt)
            if iou > biggest_iou: #近いという条件
                nearest_pt = pt
        return nearest_pt

# ただ再生したり、全てのframeにおいて、ssdモデルにかける時用
class MyVideoNormal(MyVideo): #MyVideoクラスを継承
    def __init__(self,file_path):
        self.cap = cv2.VideoCapture(file_path)
        super(MyVideoNormal,self).__init__()

# motion vectorを使う時用
class MyVideoAV(MyVideo):
    def __init__(self,file_path):
        self.video = av.open(file_path)
        super(MyVideoAV,self).__init__()


class MyFrame:
    def __init__(self,frame,key_frame,cnt,mvs = []):
        self.cnt = cnt #0-indexed
        self.data = frame
        self.key_frame = key_frame
        self.mvs = mvs

    def delete_object(self):
        self.objects.delete() #objectのnameとpercentで絞って、削除をする
    
    def embed_object_to_frame(self,objects):
        for object in objects:
            cv2.rectangle(self.data, (object.pt[0], object.pt[1]), (object.pt[2], object.pt[3]), color=object.color, thickness=2)
            cv2.putText(self.data, object.text,(object.pt[0],object.pt[1]),cv2.FONT_HERSHEY_SIMPLEX,consts.LITERAL_SIZE,object.color,int(consts.LITERAL_SIZE*2),cv2.LINE_AA)

    def embed_gt_to_frame(self,gt):
        cv2.rectangle(self.data, (gt[0],gt[1]),(gt[2],gt[3]), color = (255,255,0), thickness=2)

    def save_frame(self,myvideo):
        myvideo.out.write(self.data)

    def embed_mv(self):
        for y in range(len(self.mvs)):
            for x in range(len(self.mvs[y])):
                mv = self.mvs[y][x]
                cv2.arrowedLine(self.data, (mv[0],mv[1]), (mv[2],mv[3]), color=(0,0,255), thickness=2, line_type=cv2.LINE_8, shift=0, tipLength=0.1)

    def display_frame(self):
        # 画質が良すぎると、oepncvは描写するのにかなり時間がかかってしまうため、画質を悪くする
        # frame rateを測る時は、画面を描写せずにやると、時間が早くなりそう
        frame = imutils.resize(self.data, width=450)
        cv2.imshow("Test", frame)
        cv2.waitKey(1)

    def find_moving_object():
        return pt

class MyObject:
    def __init__(self,pt,text,color):
        self.text = text
        self.pt = pt
        self.color = color

    # 動きを計算して、次の位置を返す
    def move(self,next_pt):
        if next_pt == []:
            return
        # 動きすぎの問題と、形が変わりすぎの問題を解決して、ptをselfにセットする
        grad = consts.GRAD_FRAME #一度に動いてよい範囲(犬の動画は15ぐらいがちょうど良い)
        for i in range(4):
            if self.pt[i] - next_pt[i] >= grad:
                self.pt[i] -= grad
            elif next_pt[i] - self.pt[i] >= grad:
                self.pt[i] += grad
            else:
                self.pt[i] = next_pt[i]
            self.pt[i] = int(self.pt[i])

    def object_distance(self,myobject):
        distance = ((self.pt[0]+self.pt[2])/2 - (myobject.pt[0]+myobject.pt[2])/2)**2 + ((self.pt[1]+self.pt[3])/2 - (myobject.pt[1]+myobject.pt[3])/2)**2 
        return distance

    def caliculate_vector(self,frame,mvs):
        cnt = 0
        cntm = 0
        ave_vector = [0,0]
        for y in range(int(self.pt[1]//8),int(self.pt[3]//8)):
            for x in range(int(self.pt[0]//8),int(self.pt[2]//8)):
                cnt += 1
                mv = mvs[y][x]
                if mv != [0.0,0.0,0.0,0.0,0.0]:
                    ave_vector[0] += mv[2] - mv[0]
                    ave_vector[1] += mv[3] - mv[1]
                    cntm += 1
        ave_vector[0] /= cnt
        ave_vector[1] /= cnt

        if cntm / cnt <= 0.5: #物体のうちの動きベクトルのある範囲
            ave_vector[0] = 0
            ave_vector[1] = 0
        return ave_vector

