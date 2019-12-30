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

