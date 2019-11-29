import imutils
import cv2
import av
import numpy as np

class MyVideo:
    def __init__(self,file_path):
        self.cap = cv2.VideoCapture(file_path)
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

    def forward_frame(self,save = 0):
        myframe = self.frames[-1]
        myframe.embed_object_to_frame(self.objects)

        if save != 0:
            myframe.save_frame(self)
        myframe.display_frame()

class MyVideoAV:
    def __init__(self,file_path):
        self.video = av.open(file_path)
        self.frames = []
        self.objects = []

    def reset_objects(self):
        self.objects = []

    def init_meta_data(self,data):
        self.width = len(data[0])
        self.height = len(data)
        fourcc = cv2.VideoWriter_fourcc(*'MPEG')
        self.out = cv2.VideoWriter('output_videos/output.mp4',fourcc, 20.0, (self.width,self.height))
    
    def read_frame(self,cnt,mvs = []):
        ret,frame = self.cap.read()
        if ret == 0:
            return 0
        else:
            myframe = MyFrame(frame,0,cnt,mvs)
            self.frames.append(myframe)
            return myframe

    def finish_play(self):
        self.cap.release
        cv2.destroyAllWindows() 

    def add_object(self,my_object):
        self.objects.append(my_object)

    def forward_frame(self,save = 0):
        myframe = self.frames[-1]
        myframe.embed_object_to_frame(self.objects)

        if save != 0:
            myframe.save_frame(self)
        myframe.display_frame()

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


class MyObject:

    def __init__(self,pt,text,color):
        self.text = text
        self.pt = pt

        #self.center_x = center_x
        #self.center_y = center_y
        #self.width = width
        #self.height = height
        self.color = color

    # 動きを計算して、次の位置を返す
    def move(frame,center_x,center_y,text):
        print("move to ~~~")

        return next_x,nexty
        
    # 物体をframeに書き込む
    def draw(frame,text,x,y):
        return frame

    def set_color(color):
       self.color = color

