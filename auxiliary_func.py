# -*- coding: utf-8 -*-
"""
Created on Sun Feb 16 10:36:44 2020

@author: HP
"""

import numpy as np
from numba import jit
import os
from BresenhamAlgorithm import Pos_of_Line

@jit(nopython = True)
def go_fast(a,b,c):
    for i in range(a.shape[0]):
        for j in range(a.shape[1]):
            temp = int(a[i,j]+b)*c
            temp = max(0, temp)
            temp = min(temp,255)
            a[i,j] = temp
    return a


@jit(nopython = True)
def background_divide(a, b, c):
    if len(a.shape) == 3:
        for i in range(a.shape[0]):
            for j in range(a.shape[1]):
                for k in range(a.shape[2]):
                    temp = round(int(a[i,j,k])/(b[i,j,k]/(c[k])+0.00001))
                    if temp >=255:
                        a[i,j,k] = 255
                    else:
                        a[i,j,k] = temp                    
    return a  



@jit(nopython = True)
def matrix_divide(a,b):
    if len(a.shape) == 3:
        for i in range(a.shape[0]):
            for j in range(a.shape[1]):
                for k in range(a.shape[2]):
                    a[i,j,k] = round(a[i,j,k]/(b+0.001))
    return a



def get_folder_from_file(filename):
    folder = filename
    while folder[-1] != '/':
        folder = folder[:-1]
    return folder


@jit(nopython = True)
def float2uint8(img_aver):

    if len(img_aver.shape) == 3:
        for i in range(img_aver.shape[0]):
            for j in range(img_aver.shape[1]):
                for k in range(img_aver.shape[2]):
                    #img_aver[i,j,k] = round(img_aver[i,j,k])
                    img_aver[i,j,k] = max(0, img_aver[i,j,k])
                    img_aver[i,j,k] = min(255, img_aver[i,j,k])
    
    '''
    elif len(img_aver.shape) == 1:
        for i in range(img_aver.shape[0]):
            for j in range(img_aver.shape[1]):
                img_aver[i,j] = max(0, img_aver[i,j])
                img_aver[i,j] = min(255, img_aver[i,j])
    '''
    return img_aver.astype(np.uint8)



#@jit(nopython = True)
def calculate_contrast(matrix, x1_1, y1_1, x1_2, y1_2, x2_1, y2_1, x2_2, y2_2):
    group1_x, group1_y = Pos_of_Line(x1_1, y1_1, x1_2, y1_2)
    group2_x, group2_y = Pos_of_Line(x2_1, y2_1, x2_2, y2_2)
    color1, color2 = 0, 0
    #if len(matrix.shape) == 3:
        #matrix = matrix[:,:,1]
    if len(group1_x)>5:
        group1_x = group1_x[:-3]
        group1_y = group1_y[:-3]
        for i in range(len(group1_x)):
            x = min(group1_y[i],matrix.shape[0]-1)
            y = min(group1_x[i],matrix.shape[1]-1)
            if len(matrix.shape) == 3: 
                color1 += (matrix[x, y, 0]*0.299 + matrix[x, y, 1]*0.587 + matrix[x, y, 2]*0.114)
            else:
                color1 += matrix[x,y]
        color1 /= len(group1_x)
    else:
        return 0
    
    if len(group2_x)>5:
        group2_x = group2_x[:-3]
        group2_y = group2_y[:-3]
        for j in range(len(group2_x)):
            x = min(group2_y[j],matrix.shape[0]-1)
            y = min(group2_x[j],matrix.shape[1]-1)
            if len(matrix.shape) == 3: 
                color2 += (matrix[x, y, 0]*0.299 + matrix[x, y, 1]*0.587 + matrix[x, y, 2]*0.114)
            else:
                color2 += matrix[x,y]
        color2 /= len(group2_x)
    else:
        return 0
    
    #print (color1, color2)
    
    contrast = (color1-color2)/(color2+0.001)
    return contrast



@jit(nopython = True)
def record_draw_shape(blank, x_pos, y_pos, num):
    if len(x_pos) > 0:
        for i in range(len(x_pos)):
            if x_pos[i] < blank.shape[1] and y_pos[i] < blank.shape[0]:
                
                blank[y_pos[i], x_pos[i]] = num
            
    return blank
    


def calculate_angle(pos11,pos12,pos21,pos22):
    x11, y11 = list(pos11)[0], list(pos11)[1]
    x12, y12 = list(pos12)[0], list(pos12)[1]
    x21, y21 = list(pos21)[0], list(pos21)[1]
    x22, y22 = list(pos22)[0], list(pos22)[1]
    
    a_square = (x12 - x11)**2 + (y12 - y11)**2
    b_square = (x22 - x21)**2 + (y22 - y21)**2
    a = np.sqrt(a_square)
    b = np.sqrt(b_square)
    c_square = ((x12 - x11)-(x22 - x21))**2 + ((y12 - y11)-(y22 - y21))**2
    if a*b == 0 or a == b:
        return 0
    else:
        theta = (a_square + b_square - c_square)/(2 * a * b)
        if abs(theta) > 1:
            return 0
        theta = np.arccos(theta)
        theta = theta/np.pi*180
    return theta



if __name__ == '__main__':
    u = os.path.abspath(__file__).replace('\\','/')
    u = get_folder_from_file(u)