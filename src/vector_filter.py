import math
import numpy as np

# length_median_filterの役割も兼ねているので、こっちだけにする
def vector_median_filter(row_mvs):
    filtered_mvs = [[[[0,0,0,0,0] for x in range(len(row_mvs[0][0]))] for y in range(len(row_mvs[0]))] for k in range(len(row_mvs))]#i番目のフレームのy,x座標のmotion vector(sx,sy,dx,dy,length)の順で入っている
    for t in range(len(row_mvs)):
        print("\rprocessing frame:" + str(t),end='')
        for y in range(len(row_mvs[0])):
            for x in range(len(row_mvs[0][0])):
                ave_row = [0,0,0,0,0]
                cnti = 0
                for ti in [-1,0,1]:
                    for yi in [-2,-1,0,1,2]:
                        for xi in [-2,-1,0,1,2]:
                            if y+yi >= 0 and y+yi < len(row_mvs[0]) and x+xi >= 0 and x+xi < len(row_mvs[0][0]) and t+ti < len(row_mvs) and t+ti >= 0:
                                mv = row_mvs[t+ti][y+yi][x+xi]
                                for j in range(4):
                                    ave_row[j] += mv[j]
                                if mv != [0,0,0,0]:
                                    cnti += 1
                for j in range(4):
                    # ここをそもそもcntiで割っていたのではノイズは消せない
                    if cnti != 0:
                        filtered_mvs[t][y][x][j] = ave_row[j]//cnti
                mv_tmp = filtered_mvs[t][y][x]
                filtered_mvs[t][y][x][4] = (mv_tmp[0]-mv_tmp[2])**2 + (mv_tmp[1] - mv_tmp[3])**2
    return filtered_mvs

# このフィルタの問題点として、mvがそもそもフレーム間での正規化を行なっていないという問題がある。
# mvをどのフレームからどのフレームに向けたmvなのかを考慮して取り出す必要がありそう(取り出し方がわからない)
def temporal_median_fiter(row_mvs):
    filtered_mvs = [[[[0,0,0,0,0] for x in range(len(row_mvs[0][0]))] for y in range(len(row_mvs[0]))] for k in range(len(row_mvs))] #大きさの平均
    for t in range(len(row_mvs)):
        #print("\rprocessing frame:" + str(t),end='')
        for y in range(len(row_mvs[0])):
            for x in range(len(row_mvs[0][0])):
                mv = row_mvs[t][y][x]
                if mv == [0,0,0,0,0]:
                    continue
                print(t-1,mv[3]//8,mv[2]//8)
                mv_t_1 = row_mvs[t-1][mv[3]//8][mv[2]//8]
                mv_t_2 = [0,0,0,0,0]
                if t >= 2:
                    mv_t_2 = row_mvs[t-2][mv_t_1[3]//8][mv_t_1[2]//8]
                if tci(mv,mv_t_1,mv_t_2) > 0: #mvが使えるかどうか（ノイズかどうかを判断する）
                    for i in range(4):
                        filtered_mvs[t][y][x][i] = mv[i]
                    filtered_mvs[t][y][x][4] = (mv[0]-mv[2])**2 + (mv[1]-mv[3])**2
    return filtered_mvs

def tci(mv_t,mv_t_1,mv_t_2):
    tmp = R(mv_t,mv_t_1)*R(mv_t_1,mv_t_2)
    return math.sqrt(tmp)

def R(a,b):
    abs_a = vector_abs(a)
    abs_b = vector_abs(b)
    if abs_a == 0 and abs_b == 0:
        return 1
    else:
        a_b = [a[i] - b[i] for i in range(4)]
        return (1 - (vector_abs(a_b)/(abs_a+abs_b)))

def vector_abs(vector):
    width = vector[0] - vector[2]
    height = vector[1] - vector[3]
    return math.sqrt(width**2 + height**2)

