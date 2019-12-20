import csv
import numpy as np
import os
import consts

frame_num = consts.FRAME_NUM
frame_width = consts.FRAME_WIDTH
frame_height = consts.FRAME_HEIGHT

numpy_array_file_name = 'numpy_array/' + consts.FILE_NAME + ".npy"
numpy_array_vector_file_name = 'numpy_array/' + consts.FILE_NAME + "vector.npy"

# motion vectorの大きさのみを平均化する
def ave_mvs(frame_mvs):
    frame_mvs_ave_len= [[[0 for x in range(frame_width)] for y in range(frame_height)] for k in range(frame_num)] #大きさの平均
    frame_mvs_ave_cnt = [[[0 for x in range(frame_width)] for y in range(frame_height)] for k in range(frame_num)] #個数の平均
    for i in range(frame_num):
        print("frame_number:"+str(i))
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

#向きを考慮した平均化をする
def ave_vector_dir(frame_mvs):
    # frame_mvs_ave_vector[i][y][x] i番目のフレームのy,x座標のmotion vector(大きさ、sx,sy,yx,yy)の順で入っている
    frame_mvs_ave_vector = [[[[0,0,0,0,0] for x in range(frame_width)] for y in range(frame_height)] for k in range(frame_num)] #大きさの平均
    for i in range(frame_num):
        print("frame_number:"+str(i))
        for y in range(frame_height):
            for x in range(frame_width):
                ave_row = [0,0,0,0,0]
                for yi in [-2,-1,0,1,2]:
                    for xi in [-2,-1,0,1,2]:
                        if y+yi >= 0 and y+yi < frame_height and x+xi >= 0 and x+xi < frame_width:
                            for mv in frame_mvs[i][y+yi][x+xi]:
                                for j in range(4):
                                    ave_row[j] += mv[j+3]
                                ave_row[4] += ((mv[3]-mv[5])**2 + (mv[4]-mv[6])**2)
                for j in range(5):
                    #print(i,y,x,j)
                    frame_mvs_ave_vector[i][y][x][j] = ave_row[j] / 25

    np.save(numpy_array_vector_file_name, np.array(frame_mvs_ave_vector))
    return frame_mvs_ave_vector

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

                for i in range(7):
                    row[i] = int(row[i])

                frame_mvs[frame_cnt][y][x].append(row)

                mvs[frame_cnt].append(row)
                line_count += 1
        print(f'Processed {line_count} lines.')

    if consts.VECTOR_DIR:
        frame_mvs = ave_vector_dir(frame_mvs)
    else:
        frame_mvs = ave_mvs(frame_mvs)
    print("finish caliculating average")
    return frame_mvs

if __name__ == '__main__':
    read_csv("mv_csv/car.csv")

