import csv
import numpy as np
import os

# vtest.mp4
#frame_num = 800
#frame_width = 100 #pxを8で割った値に少し余裕を持たせておく
#frame_height = 100

# dog_out.mp4
frame_num = 301
frame_width = 170 #pxを8で割った値に少し余裕を持たせておく
frame_height = 100

# bike.mp4
#frame_num = 150
#frame_width = 83 #pxを8で割った値に少し余裕を持たせておく
#frame_height = 53

# car.mp4
#frame_num = 1021
#frame_width = 50
#frame_height = 100

numpy_array_file_name = 'numpy_array/' # main.pyの中で書き換える

# motion vectorを平均化する
def ave_mvs(frame_mvs):
    if os.path.exists(numpy_array_file_name): #このファイルがある場合は毎回計算せず、numpyをファイルから呼び出す。そうなので、新しく計算し直す時はこのファイルを消してから実行する
        frame_mvs_ave_cnt = np.load(file=numpy_array_file_name).tolist()
        return frame_mvs_ave_cnt
    frame_mvs_ave_len= [[[0 for x in range(frame_width)] for y in range(frame_height)] for k in range(frame_num)] #大きさの平均
    frame_mvs_ave_cnt = [[[0 for x in range(frame_width)] for y in range(frame_height)] for k in range(frame_num)] #個数の平均
    for i in range(frame_num):
        for y in range(frame_height):
            for x in range(frame_width):
                mv_len_sum = 0
                mv_cnt_sum = 0
                for yi in [-2,-1,0,1,2]:
                    for xi in [-2,-1,0,1,2]:
                        if y+yi >= 0 and y+yi < frame_height and x+xi >= 0 and x+xi < frame_width:
                            mv_cnt_sum += len(frame_mvs[i][y+yi][x+xi])
                            for mv in frame_mvs[i][y+yi][x+xi]:
                                mv_len_sum += ((mv[3]-mv[5])**2 + (mv[4]-mv[5])**2)
                frame_mvs_ave_cnt[i][y][x] = mv_cnt_sum / 9
                frame_mvs_ave_len[i][y][x] = mv_len_sum / 9
    np.save(numpy_array_file_name, np.array(frame_mvs_ave_cnt))
    return frame_mvs_ave_cnt

def read_csv(csv_file_path):
    mvs = [[] for i in range(frame_num)] # mv[i][j][k] #i: frameの番号, j: i番目のフレームのj番目のmv, k: mvの属性

    frame_mvs= [[[[] for x in range(frame_width)] for y in range(frame_height)] for k in range(frame_num)] #frame_mvs[i][y][x][t] i : frame番号, x,yはフレームの座標(8x8), t: マクロブロックの中のmotion vector

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

                x = int(int(row[3])/8)
                y = int(int(row[4])/8)
                #print(x,y)
                row[0] = int(row[0])
                row[1] = int(row[1])
                row[2] = int(row[2])
                row[3] = int(row[3])
                row[4] = int(row[4])
                row[5] = int(row[5])
                row[6] = int(row[5])

                frame_mvs[frame_cnt][y][x].append(row)

                mvs[frame_cnt].append(row)
                line_count += 1
        print(f'Processed {line_count} lines.')

    frame_mvs = ave_mvs(frame_mvs)
    print("finish caliculating average")
    return frame_mvs

if __name__ == '__main__':
    read_csv("mv_csv/car.csv")

