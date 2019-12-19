from __future__ import division
import time
import torch
import torch.nn as nn
from torch.autograd import Variable
import numpy as np
import cv2
from util import *
from darknet import Darknet
from preprocess import prep_image, inp_to_image
import pandas as pd
import random
import pickle as pkl
 
def prep_image(img, inp_dim):
    # CNNに通すために画像を加工する
    orig_im = img
    dim = orig_im.shape[1], orig_im.shape[0]
    img = cv2.resize(orig_im, (inp_dim, inp_dim))
    img_ = img[:,:,::-1].transpose((2,0,1)).copy()
    img_ = torch.from_numpy(img_).float().div(255.0).unsqueeze(0)
    return img_, orig_im, dim
 
def write(x, img):
    # 画像に結果を描画
    c1 = tuple(x[1:3].int())
    c2 = tuple(x[3:5].int())
    cls = int(x[-1])
    label = "{0}".format(classes[cls])
    color = random.choice(colors)
    cv2.rectangle(img, c1, c2,color, 1)
    t_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_PLAIN, 1 , 1)[0]
    c2 = c1[0] + t_size[0] + 3, c1[1] + t_size[1] + 4
    #cv2.rectangle(img, c1, c2,color, -1)
    #cv2.putText(img, label, (c1[0], c1[1] + t_size[1] + 4), cv2.FONT_HERSHEY_PLAIN, 1, [225,255,255], 1);
    return 
    return img
 
cfgfile = "cfg/yolov3.cfg" # 設定ファイル
weightsfile = "weights/yolov3.weights" # 重みファイル
num_classes = 80 # クラスの数
 
num_classes = 80 # クラスの数
bbox_attrs = 5 + num_classes

model = Darknet(cfgfile) #modelの作成
model.load_weights(weightsfile) # modelに重みを読み込む
inp_dim = int(model.net_info["height"])
 
assert inp_dim % 32 == 0
assert inp_dim > 32

CUDA = torch.cuda.is_available() # CUDAが使用可能かどうか

if CUDA:
    model.cuda() #CUDAが使用可能であればcudaを起動

model.eval()

def detect_from_yolo(frame,cnt):
    img, orig_im, dim = prep_image(frame, inp_dim)

    if CUDA:
        im_dim = im_dim.cuda()
        img = img.cuda()

    output = model(Variable(img), CUDA)
    output = write_results(output, confidence, num_classes, nms = True, nms_conf = nms_thesh)

    # FPSの表示
    if type(output) == int:
        cv2.imshow("frame", orig_im)

        # qキーを押すとFPS表示の終了
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break
        continue

    output[:,1:5] = torch.clamp(output[:,1:5], 0.0, float(inp_dim))/inp_dim
    output[:,[1,3]] *= frame.shape[1]
    output[:,[2,4]] *= frame.shape[0]

    classes = load_classes('data/coco.names') # 識別クラスのリスト
    colors = pkl.load(open("pallete", "rb"))

    # ここでptsとdisplay txtを返す
    return list(map(lambda x: write(x, orig_im), output))
     
