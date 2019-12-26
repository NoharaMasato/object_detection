import os
import sys
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)
 
import torch
import torch.nn as nn
from torch.autograd import Variable
import numpy as np
import cv2
import glob
from ssd import build_ssd
import read_csv
import consts
import sys
sys.setrecursionlimit(10000)

 
frame_num = read_csv.frame_num
frame_width = read_csv.frame_width
frame_height = read_csv.frame_height

mv_len_threash = consts.MV_THREASH

# SSDモデルを読み込み
net = build_ssd('test', 300, 21)   
net.load_weights('weights/ssd300_mAP_77.43_v2.pth')

nx = [0,0,1,-1]
ny = [1,-1,0,0]

grouping_cnt = 0
grouping = [[0 for x in range(frame_width)] for y in range(frame_height)]
grouping_draw = [[0 for x in range(frame_width)] for y in range(frame_height)]
grouping_pt= [[0 for x in range(frame_width)] for y in range(frame_height)]

def draw_block(frame,x,y):
    cv2.rectangle(frame, (x*8, y*8), ((x+1)*8, (y+1)*8), color=(255, 0, 0), thickness=-1) # thickness = -1は塗りつぶす

def dfs(nowx,nowy,mvs):
    global grouping,grouping_cnt
    grouping[nowy][nowx] = grouping_cnt

    node_cnt = 0
    for i in range(4):
        nextx = nowx + nx[i]
        nexty = nowy + ny[i]
        if (nextx>=0 and nexty>=0 and nextx < frame_width and nexty < frame_height and mvs[nowy][nowx][4] > mv_len_threash and grouping[nexty][nextx] == 0):
            node_cnt+=dfs(nextx,nexty,mvs)

    return node_cnt + 1

# threashholdより大きいもののみ塗る
def dfs_draw(nowx,nowy,mvs,frame):
    global grouping_draw,grouping_cnt
    if mvs[nowy][nowx][4] > mv_len_threash:
        cv2.rectangle(frame, (nowx*8, nowy*8), ((nowx+1)*8, (nowy+1)*8), color=(255, 0, 0), thickness=-1) # thickness = -1は塗りつぶす
        grouping_draw[nowy][nowx] = grouping_cnt
        for i in range(4):
            nextx = nowx + nx[i]
            nexty = nowy + ny[i]
            if (nextx>=0 and nexty>=0 and mvs[nowy][nowx][4] > mv_len_threash and grouping_draw[nexty][nextx] == 0):
                dfs_draw(nextx,nexty,mvs,frame)

now_dt = []
def dfs_cnt_pt(nowx,nowy,mvs):
    if mvs[nowy][nowx][4] > mv_len_threash:
        global grouping_pt,grouping_cnt
        grouping_pt[nowy][nowx] = grouping_cnt
        global now_dt
        if nowx < now_dt[0]:
            now_dt[0] = nowx
        if nowx > now_dt[2]:
            now_dt[2] = nowx
        if nowy < now_dt[1]:
            now_dt[1] = nowy
        if nowy > now_dt[3]:
            now_dt[3] = nowy

        for i in range(4):
            nextx = nowx + nx[i]
            nexty = nowy + ny[i]
            if (nextx>=0 and nexty>=0 and mvs[nowy][nowx][4] > mv_len_threash and grouping_pt[nexty][nextx] == 0):
                dfs_cnt_pt(nextx,nexty,mvs)

def detect_from_mv(frame,cnt,mvs):
    global grouping_cnt
    global grouping,grouping_draw,grouping_pt

    grouping_cnt = 1
    for y in range(frame_height):
        for x in range(frame_width):
            grouping[y][x] = 0
            grouping_draw[y][x] = 0
            grouping_pt[y][x] = 0

    node_cnt = 0
    pts = []
    for y in range(frame_height):
        for x in range(frame_width):
            if mvs[y][x][4] > mv_len_threash and grouping[y][x] == 0:
                cnt = dfs(x,y,mvs)
                if consts.DRAW_MV:
                    dfs_draw(x,y,mvs,frame) #ここで、mvの色を塗るかどうかを決める
                if cnt >= 100:
                    grouping_cnt += 1
                    global now_dt
                    now_dt = [x,y,x,y]
                    dfs_cnt_pt(x,y,mvs)
                    now_dt[0] *= 8
                    now_dt[1] *= 8
                    now_dt[2] *= 8
                    now_dt[2] += 8
                    now_dt[3] *= 8
                    now_dt[3] += 8
                    pts.append(now_dt)
    return pts

# 関数 detect    
def detect_from_ssd(image, count):
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    x = cv2.resize(image, (300, 300)).astype(np.float32)  # 300*300にリサイズ
    x -= (104.0, 117.0, 123.0)
    x = x.astype(np.float32)
    x = x[:, :, ::-1].copy()
    x = torch.from_numpy(x).permute(2, 0, 1)  # [300,300,3]→[3,300,300]
    xx = Variable(x.unsqueeze(0))     # [3,300,300]→[1,3,300,300]    
    # 順伝播を実行し、推論結果を出力    
    y = net(xx)
 
    from data import VOC_CLASSES as labels
    # 推論結果をdetectionsに格納
    detections = y.data
    # scale each detection back up to the image
    scale = torch.Tensor(rgb_image.shape[1::-1]).repeat(2)
    
    # バウンディングボックスとクラス名を表示
    pts = []
    display_txts = []
    for i in range(detections.size(1)):
        j = 0
        # 確信度confが0.6以上のボックスを表示
        # jは確信度上位200件のボックスのインデックス
        # detections[0,i,j]は[conf,xmin,ymin,xmax,ymax]の形状
        while detections[0,i,j,0] >= 0.6:
            score = detections[0,i,j,0]
            label_name = labels[i-1]
            display_txt = '%s: %.2f'%(label_name, score)
            pt = (detections[0,i,j,1:]*scale).cpu().numpy()
            coords = (pt[0], pt[1]), pt[2]-pt[0]+1, pt[3]-pt[1]+1
            pts.append(pt)
            display_txts.append(display_txt)
            #color = colors[i]
            #cv2.rectangle(image, (pt[0], pt[1]), (pt[2], pt[3]), color=(0, 255, 0), thickness=2)
            #cv2.putText(image, display_txt,(pt[0],pt[1]),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2,cv2.LINE_AA)
            j+=1
    return pts,display_txts
 
def main():
    files = sorted(glob.glob('./image_dir/*.png'))
    count = 1
    for i, file in enumerate (files):
        image = cv2.imread(file, cv2.IMREAD_COLOR)          
        detect(image, count)
        print(count)
        count +=1
 
if __name__ == '__main__':
    main()  

