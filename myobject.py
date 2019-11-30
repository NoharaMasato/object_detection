import imutils
import cv2
import av
import numpy as np

class MyVideo:
    def __init__(self):
        self.frames = []
        self.objects = []

    def reset_objects(self):
        self.objects = []
    
    def read_frame(self,cnt,mvs = []):
        ret,frame = self.cap.read()
        if ret == 0:
            return 0
        else:
            myframe = MyFrame(frame,0,cnt,mvs)
            self.frames.append(myframe)
            return myframe

    def init_meta_data(self,data):
        self.width = len(data[0])
        self.height = len(data)
        fourcc = cv2.VideoWriter_fourcc(*'MPEG')
        self.out = cv2.VideoWriter('output_videos/output.mp4',fourcc, 20.0, (self.width,self.height))

    def finish_play(self):
        self.cap.release
        cv2.destroyAllWindows() 

    def add_object(self,my_object):
        self.objects.append(my_object)

    def forward_frame(self,save = 0,play = 1):
        myframe = self.frames[-1]
        myframe.embed_object_to_frame(self.objects)

        if save != 0:
            myframe.save_frame(self)
        if play != 0:
            myframe.display_frame()

    def is_objects_overlaped(self):
        myobjects = self.objects
        for i in range(len(myobjects)):
            for j in range(i+1,len(myobjects)):
                # i番目のmyobjectとj番目のobjectとかぶっていないかをチェックする
                if myobjects[i].object_distance(myobjects[j]) < 200:
                    return True
        return False

    # myobjectに適したptsを候補のptsから選び、戻り値として返す
    def select_nearest_pt(self,pts,myobject):
        before_pt = myobject.pt
        # ptsの中からbefore_ptに一番近いものを選ぶ
        nearest_pt = []
        nearest_distance = 10000000 
        for pt in pts:
            distance = (pt[0]+pt[2]-(before_pt[0]-before_pt[2]))**2 + (pt[1]+pt[3]-(before_pt[1]-before_pt[3]))**2
            if distance < nearest_distance: #近いという条件
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
        self.cnt = cnt
        self.data = frame
        self.key_frame = key_frame
        self.mvs = mvs
        

    def delete_object(self):
        self.objects.delete() #objectのnameとpercentで絞って、削除をする
    
    def embed_object_to_frame(self,objects):
        for object in objects:
            cv2.rectangle(self.data, (object.pt[0], object.pt[1]), (object.pt[2], object.pt[3]), color=object.color, thickness=2)
            cv2.putText(self.data, object.text,(object.pt[0],object.pt[1]),cv2.FONT_HERSHEY_SIMPLEX,1,object.color,2,cv2.LINE_AA)

    def save_frame(self,myvideo):
        myvideo.out.write(self.data)

    def embed_mv(self):
        for y in range(len(self.mvs)):
            for x in range(len(self.mvs[y])):
                mv = self.mvs[y][x]
                if (mv > 0):
                    cv2.rectangle(self.data, (x*8, y*8), ((x+1)*8, (y+1)*8), color=(0,0,255), thickness=-1)

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
        # 動きすぎの問題と、形が変わりすぎの問題を解決して、ptをselfにセットする
        grad = 15 #一度に動いてよい範囲(犬の動画は15ぐらいがちょうど良い)
        for i in range(4):
            if self.pt[i] - next_pt[i] >= grad:
                self.pt[i] -= grad
            elif next_pt[i] - self.pt[i] >= grad:
                self.pt[i] += grad
            else:
                self.pt[i] = next_pt[i]

    def object_distance(self,myobject):
        distance = ((self.pt[0]+self.pt[2])/2 - (myobject.pt[0]+myobject.pt[2])/2)**2 + ((self.pt[1]+self.pt[3])/2 - (myobject.pt[1]+myobject.pt[3])/2)**2 
        return distance

