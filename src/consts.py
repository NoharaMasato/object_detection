PLAY = 1
SAVE = 1

SSD = 1
YOLO = 0
if SSD + YOLO != 1:
    print("SSD or YOLOのどちらかを1にしてください")
    exit(0)

DRAW_MV = 1

VECTOR_DIR = 0 # 0の場合はベクトルの大きさだけを考慮する 

# MV_FILTERを決める
#FILTER = "MEDIAN"
#FILTER = "TF"
FILTER = ""

OBT = 0 #OBTのデータセットを使うかどうか

ACCURACY = 0 #精度を求めるか(現在は犬の動画しかground truthを取っていないためその他の動画では不可能)
if ACCURACY == 1:
    USE_mAP50 = 1
    ACCURACY_PRINT = 0 #精度を毎回表示するか
    I_INTER_VALS = [1,2,3,4,5,6,7,8,9,10,20,30,40,50,60,70,80,90,100,150]

# dog outだと5が精度が良くなる
MV_THREASH = 0 #mvの大きさのスレッシュホールド

CONSIDER_OVERLAPPED = 1 #objectが重なっている時(ある一定以上近い時)にもう一度物体認識にかけるかどうか


#FILE_NAME = "vtest"
FILE_NAME = "dog_out"
#FILE_NAME = "David3"
#FILE_NAME = "bike"
#FILE_NAME = "car"
#FILE_NAME = "kanshi"
#FILE_NAME = "kanshi2"
#FILE_NAME = "kanshi3"
#FILE_NAME = "walk"
#FILE_NAME = "walk1"

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
    LITERAL_SIZE = 0.5

elif FILE_NAME == "kanshi2":
    FRAME_NUM = 901
    FRAME_WIDTH = 100
    FRAME_HEIGHT = 50
    GRAD_FRAME = 15
    LITERAL_SIZE = 1

elif FILE_NAME == "kanshi3":
    FRAME_NUM = 764
    FRAME_WIDTH = 100
    FRAME_HEIGHT = 50
    GRAD_FRAME = 15
    LITERAL_SIZE = 1

elif FILE_NAME == "walk":
    FRAME_NUM = 413
    FRAME_WIDTH = 100
    FRAME_HEIGHT = 100
    GRAD_FRAME = 15
    LITERAL_SIZE = 1

elif FILE_NAME == "walk1":
    FRAME_NUM = 675
    FRAME_WIDTH = 250
    FRAME_HEIGHT = 150
    GRAD_FRAME = 15
    LITERAL_SIZE = 1

elif FILE_NAME == "David3":
    FRAME_NUM = 253
    FRAME_WIDTH = 90
    FRAME_HEIGHT = 65
    GRAD_FRAME = 15
    LITERAL_SIZE = 1
