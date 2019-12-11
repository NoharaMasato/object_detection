DRAW_MV = 0
VECTOR_DIR = 0

#FILE_NAME = "vtest"
#FILE_NAME = "dog_out"
#FILE_NAME = "bike"
#FILE_NAME = "car"
FILE_NAME = "kanshi"

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

