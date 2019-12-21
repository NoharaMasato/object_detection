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
 
cfgfile = "cfg/yolov3.cfg" # 設定ファイル
weightsfile = "weights/yolov3.weights" # 重みファイル
num_classes = 80 # クラスの数
bbox_attrs = 5 + num_classes

confidence = 0.25
nms_thesh = 0.4

model = Darknet(cfgfile) #modelの作成
model.load_weights(weightsfile) # modelに重みを読み込む
model.net_info["height"] = 160
inp_dim = int(model.net_info["height"])
 
classes = load_classes('data/coco.names') # 識別クラスのリスト
colors = pkl.load(open("yolo/pallete", "rb"))

assert inp_dim % 32 == 0
assert inp_dim > 32

CUDA = torch.cuda.is_available() # CUDAが使用可能かどうか

if CUDA:
    model.cuda() #CUDAが使用可能であればcudaを起動

model.eval()

def prep_image(img, inp_dim):
    # CNNに通すために画像を加工する
    orig_im = img
    dim = orig_im.shape[1], orig_im.shape[0]
    img = cv2.resize(orig_im, (inp_dim, inp_dim))
    img_ = img[:,:,::-1].transpose((2,0,1)).copy()
    img_ = torch.from_numpy(img_).float().div(255.0).unsqueeze(0)
    return img_, orig_im, dim
 
def write(x):
    # 画像に結果を描画
    c1 = tuple(x[1:3].int())
    c2 = tuple(x[3:5].int())
    cls = int(x[-1])

    if cls >= 0 and cls < len(classes):
        label = "{0}".format(classes[cls])
    else:
        label = ""
    pt = [0,0,0,0]
    pt[0] = int(c1[0])
    pt[1] = int(c1[1])
    pt[2] = int(c2[0])
    pt[3] = int(c2[1])
    return pt,label
 

def detect_from_yolo(frame,cnt):
    img, orig_im, dim = prep_image(frame, inp_dim)

    if CUDA:
        im_dim = im_dim.cuda()
        img = img.cuda()

    output = model(Variable(img), CUDA)
    output = write_results(output, confidence, num_classes, nms = True, nms_conf = nms_thesh)

    output[:,1:5] = torch.clamp(output[:,1:5], 0.0, float(inp_dim))/inp_dim
    output[:,[1,3]] *= frame.shape[1]
    output[:,[2,4]] *= frame.shape[0]

    # ここでptsとdisplay txtsを返す
    pts = []
    display_txts = []
    for x in output:
        if x[-1]:
            pt, display_txt = write(x)
            pts.append(pt)
            display_txts.append(display_txt)
    return pts,display_txts;

