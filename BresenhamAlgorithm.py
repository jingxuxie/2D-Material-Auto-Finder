# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 19:29:59 2019

@author: HP
"""
import numpy as np
import cv2
import time
from numba import jit

@jit(nopython = True)
def Pos_of_Line(x0,y0,x1,y1):
    xindex = []
    yindex = []
    dx = abs(x1-x0)
    dy = abs(y1-y0)
    InclineRate = 0#斜率小于45度
    if dx < dy:
        InclineRate = 1#斜率大于45度
        x0,y0 = y0,x0
        x1,y1 = y1,x1
        dx,dy = dy,dx
    x = x0
    y = y0
    d = dy*2 - dx
    
    if (x1 - x0) > 0:
        ix = 1
    else:
        ix =- 1
    if (y1 - y0) > 0:
        iy = 1
    else:
        iy = -1
    if InclineRate == 0:  
        while (x != x1):
            if d < 0:
                d += dy*2
            else:
                d += (dy - dx)*2
                y += iy
            #cv2.circle(img,(x,y),1,(0,0,255))
            x += ix
            xindex.append(x)
            yindex.append(y)
    if InclineRate == 1:  
        while (x != x1):
            if d < 0:
                d += dy*2
            else:
                d += (dy - dx)*2
                y += iy
            #cv2.circle(img,(y,x),1,(0,0,255))
            x += ix
            xindex.append(y)
            yindex.append(x)
    if len(xindex) == 0:
        return [x0], [y0]
    return xindex, yindex

@jit(nopython = True)
def Pos_of_Circle(x0,y0,r):
    x = 0
    y = r
    d = 3 - 2*r
    
    xindex_temp = [x]
    yindex_temp = [y]
    
    while x <= y:
        if d < 0:
            d += 4*x + 6
            yindex_temp.append(y)
        else:
            d += 4*(x - y) + 10
            y -= 1
            yindex_temp.append(y)
        x += 1
        xindex_temp.append(x)
    
    xindex_temp = np.array(xindex_temp)
    yindex_temp = np.array(yindex_temp)
    
    x_upper_right = np.hstack((xindex_temp, yindex_temp))
    y_upper_right = np.hstack((yindex_temp, xindex_temp))
    
    x_half_right = np.hstack((x_upper_right, x_upper_right))
    y_half_right = np.hstack((y_upper_right, -y_upper_right))
    
    x_index = np.hstack((x_half_right, -x_half_right))
    y_index = np.hstack((y_half_right, y_half_right))
    
    x_index += x0
    y_index += y0
    
    #print(len(x_index),len(y_index))
    #xindex.append(xindex)
    return x_index, y_index
    
@jit(nopython = True)
def Pos_in_Circle(x0,y0,r):
    x = 0
    y = r
    d = 3 - 2*r
    
    xindex_temp = [x]
    yindex_temp = [y]
    
    while x <= y:
        for yi in range(x, y+1):
            xindex_temp.append(x)
            yindex_temp.append(yi)
        if d < 0:
            d += 4*x + 6
            yindex_temp.append(y)
        else:
            d += 4*(x - y) + 10
            y -= 1
            yindex_temp.append(y)
        x += 1
        xindex_temp.append(x)
    
    xindex_temp = np.array(xindex_temp)
    yindex_temp = np.array(yindex_temp)
    
    x_upper_right = np.hstack((xindex_temp, yindex_temp))
    y_upper_right = np.hstack((yindex_temp, xindex_temp))
    
    x_half_right = np.hstack((x_upper_right, x_upper_right))
    y_half_right = np.hstack((y_upper_right, -y_upper_right))
    
    x_index = np.hstack((x_half_right, -x_half_right))
    y_index = np.hstack((y_half_right, y_half_right))
    
    x_index += x0
    y_index += y0
    
    return x_index, y_index

        #cv2.circle(img,(x0+x,y0+y),1,(0,0,255))
        #print(x0 +x, y)
   
def Pos_of_Rec(x1, y1, x2, y2):
    width = abs(x2 - x1)
    height = abs(y2 - y1)
    
    x_index = np.array([])
    y_index = np.array([])
    
    horizontal_x = np.linspace(x1, x2, width +1, dtype = int)
    top_y = np.zeros(width + 1, dtype = int) + y1
    bottom_y = np.zeros(width + 1, dtype = int) + y2
    
    horizontal_x = np.hstack((horizontal_x,horizontal_x))
    horizontal_y = np.hstack((top_y, bottom_y))
    
    vertical_y = np.linspace(y1, y2, height + 1, dtype = int)
    left_x = np.zeros(height + 1, dtype = int) + x1
    right_x = np.zeros(height + 1, dtype = int) + x2
    
    vertical_x = np.hstack((left_x, right_x))
    vertical_y = np.hstack((vertical_y, vertical_y))
    
    x_index = np.hstack((horizontal_x, vertical_x))
    y_index = np.hstack((horizontal_y, vertical_y))
    

    return x_index, y_index
    
    
    
     
if __name__ == '__main__':
    time_start = time.time()
    img = np.zeros((600,600,3), np.uint8)
    #img1=img.copy()
    #cv2.namedWindow('image')
    #cv2.moveWindow('image',0,0)
    '''
    xtemp,ytemp=Bresenham_Algorithm_Line(200,100,100,500)
    for i in range(len(xtemp)):
        cv2.circle(img,(xtemp[i],ytemp[i]),1,(0,0,255))
    '''
    for i in range(10000):
        x_temp, y_temp = Pos_in_Circle(300,200,10)
        x_temp, y_temp = Pos_of_Circle(300,200,10)
        x_temp, y_temp = Pos_of_Rec(500,100,1000,2000)
        x_temp, y_temp = Pos_of_Line(500,100,1000,2000)
#    for i in range(len(x_temp)):
#        cv2.circle(img, (x_temp[i], y_temp[i]), 1, (0,0,255), -1)
#    cv2.imshow('image',img)  
#    k = cv2.waitKey(2000)
    
#    cv2.destroyAllWindows()
    
    time_end = time.time()
    print(time_end - time_start)