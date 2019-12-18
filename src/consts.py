PLAY = 1
SAVE = 0

DRAW_MV = 0
VECTOR_DIR = 1
ACCURACY = 1 #精度を求めるか(現在は犬の動画しかground truthを取っていないためその他の動画では不可能)
MV_THREASH = 0.3 #mvの大きさのスレッシュホールド

CONSIDER_OVERLAPPED = 1 #objectが重なっている時(ある一定以上近い時)にもう一度物体認識にかけるかどうか

#FILE_NAME = "vtest"
FILE_NAME = "dog_out"
#FILE_NAME = "bike"
#FILE_NAME = "car"
#FILE_NAME = "kanshi"
#FILE_NAME = "kanshi2"

if FILE_NAME == "vtest":
    FRAME_NUM = 800 #frame数+1にする
    FRAME_WIDTH = 100
    FRAME_HEIGHT = 100
    GRAD_FRAME = 15
    LITERAL_SIZE = 1

elif FILE_NAME == "dog_out":
    FRAME_NUM = 301
    FRAME_WIDTH = 170
    FRAME_HEIGHT = 100
    GRAD_FRAME = 15 # 1フレームで動いて良い距離
    LITERAL_SIZE = 1

elif FILE_NAME == "bike":
    FRAME_NUM = 150
    FRAME_WIDTH = 83 #pxを8で割った値に少し余裕を持たせておく
    FRAME_HEIGHT = 53
    GRAD_FRAME = 15
    LITERAL_SIZE = 1

elif FILE_NAME == "car":
    FRAME_NUM = 1021
    FRAME_WIDTH = 50
    FRAME_HEIGHT = 100
    GRAD_FRAME = 15 
    LITERAL_SIZE = 1

elif FILE_NAME == "kanshi":
    FRAME_NUM = 901
    FRAME_WIDTH = 100
    FRAME_HEIGHT = 50
    GRAD_FRAME = 15 
    LITERAL_SIZE = 1

elif FILE_NAME == "kanshi2":
    FRAME_NUM = 901
    FRAME_WIDTH = 100
    FRAME_HEIGHT = 50
    GRAD_FRAME = 15 
    LITERAL_SIZE = 1
