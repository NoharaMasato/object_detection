import csv
import numpy as np
import os
import consts
import vector_filter
import subprocess

frame_num = consts.FRAME_NUM
frame_width = consts.FRAME_WIDTH
frame_height = consts.FRAME_HEIGHT

filtered_numpy_file_name = 'numpy_array/' + consts.FILE_NAME + consts.FILTER + ".npy" #filterとファイル名でnumpy arrayを保存する

##############vectorを読み込む方針######################
# 1. 8x8単位のmacroblockで読み込む
# 2. 一つのmacroblockに複数のmvがある場合があるが、その場合は一つのvectorに合成する
# 3. sourceが１の場合はsourceとdestinationを逆にする
#################################### 
def parse_mv_from_csv(csv_file_path):
    row_mvs = [[[[0,0,0,0] for x in range(frame_width)] for y in range(frame_height)] for k in range(frame_num)] #大きさの平均
    with open(csv_file_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                frame_cnt= int(row[0].split()[-1])
                row.pop(0)
                x = int(row[3])//8
                y = int(row[4])//8

                for i in range(7):
                    row[i] = int(row[i])

                if row[1] == 1: #sourceが逆のものはひっくり返しておく
                    row[3],row[5] = row[5],row[3]
                    row[4],row[6] = row[6],row[4]
                    
                if row_mvs[frame_cnt][y][x] == [0,0,0,0]:
                    for i in range(4):
                        row_mvs[frame_cnt][y][x][i] = row[i+3]
                else:
                    row_mvs[frame_cnt][y][x][2] += (row[5] - row[3])
                    row_mvs[frame_cnt][y][x][3] += (row[6] - row[4])

                line_count += 1
        print(f'Processed {line_count} lines.')
    return row_mvs

def read_filtered_mv_from_csv(csv_file_path):
    if os.path.exists(filtered_numpy_file_name):#もうnumpyとしてある場合はここで読み込む:
        mvs = np.load(file=filtered_numpy_file_name).tolist()
    else:
        if not os.path.exists(csv_file_path):#csvがない場合はここで作る
            subprocess.call(["./extract_mvs","obt/"+consts.FILE_NAME + ".mp4",">","mv_csv/" + consts.FILE_NAME + ".csv"]) 
        row_mvs = parse_mv_from_csv(csv_file_path)
        if consts.FILTER == "MEDIAN":
            mvs = vector_filter.vector_median_filter(row_mvs)
        elif consts.FILTER == "TF":
            mvs = vector_filter.temporal_median_fiter(row_mvs)
        elif consts.FILTER == "":
            mvs = vector_filter.no_filter(row_mvs)
        print("finish filtering motion vectors")
        np.save(filtered_numpy_file_name, np.array(mvs))
    return mvs

if __name__ == '__main__':
     read_filtered_mv_from_csv("mv_csv/walk.csv")

