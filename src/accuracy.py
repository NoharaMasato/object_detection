import consts
import matplotlib.pyplot as plt

def bb_iou(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    interArea = abs(max((xB - xA, 0)) * max((yB - yA), 0))
    if interArea == 0:
        return 0
    boxAArea = abs((boxA[2] - boxA[0]) * (boxA[3] - boxA[1]))
    boxBArea = abs((boxB[2] - boxB[0]) * (boxB[3] - boxB[1]))
    iou = interArea / float(boxAArea + boxBArea - interArea)
    return iou

def parse_obt_gts(gts):
    ret_gt = []
    for gt in gts:
        if len(gt) != 4:
            continue
        src_x = int(gt[0])
        src_y = int(gt[1])
        width = int(gt[2])
        height = int(gt[3])
        ret_gt.append([src_x,src_y,src_x + width,src_y + height]) 
    return ret_gt

#ptsの中から最もgtと最もIoUが高いものを選んで、IoUを返す
def calculate_biggest_iou(pts,gt):
    biggest_iou = 0.0
    for pt in pts:
        iou = bb_iou(gt,pt)
        if iou > biggest_iou: #近いという条件
            biggest_iou = iou
    return biggest_iou 

def show_graph(elapsed_times,accuracies):
    for x,y,k in zip(elapsed_times,accuracies,sorted(consts.I_INTER_VALS*2)):
        x = 300 // x #time -> FPS
        if y[1] == 1: #動きベクトルを使わない方
            plt.plot(x,y[0],'o',color='Cyan')
        if y[1] == 0: #動きベクトルを使う方
            plt.plot(x,y[0],'o',color='Red')
        plt.annotate(str(300//k), xy=(x,y[0]))

    plt.xlabel('through put [FPS]')
    if consts.USE_mAP50:
        plt.ylabel('mAP50')
    else:
        plt.ylabel('accuracy')
    plt.savefig('figure.png')

