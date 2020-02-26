# -*- coding: utf-8 -*-
"""
Created on Sat Feb  8 10:19:00 2020

@author: HP
"""

import numpy as np
import cv2
from matplotlib import pyplot as plt
import scipy.signal as signal

img = cv2.imread('F:/2020/1/21/01-21-2020-121.jpg')
hsv = img#cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

cv2.imshow('B', img[:,:,0])
cv2.imshow('G', img[:,:,1])

#--- find Otsu threshold on hue and saturation channel ---
ret, thresh_B = cv2.threshold(hsv[:,:,0], 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
ret, thresh_G = cv2.threshold(hsv[:,:,1], 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

#--- add the result of the above two ---
cv2.imshow('thresh',  thresh_B)

out = thresh_G

#kernel_open = np.ones((5,5),np.uint8)
#img_open = cv2.morphologyEx(out, cv2.MORPH_OPEN, kernel_open)

kernel_close = np.ones((15,15),np.uint8)
img_close = cv2.morphologyEx(out, cv2.MORPH_CLOSE, kernel_close)

#img_close = np.zeros((512,512), dtype = np.uint8)
#img_close[100:200,100:200] = 100
#edge = cv2.Canny(img[:,:,1],50,150,apertureSize = 3)
#cv2.imshow('edge',edge)
'''
minLineLength = 30
maxLineGap = 0
lines = cv2.HoughLinesP(edge,1,np.pi/180,10,minLineLength,maxLineGap)
for line in lines:
    x1, y1, x2, y2 = line[0]
    cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)
    '''
#lsd = cv2.createLineSegmentDetector(0)
#lines = lsd.detect(edge)[0]
#drawn_img = lsd.drawSegments(img,lines)
#cv2.imshow('lsd', drawn_img)
'''
lines = cv2.HoughLines(edge,1,np.pi/180,200)
for rho,theta in lines[0]:
    a = np.cos(theta)
    b = np.sin(theta)
    x0 = a*rho
    y0 = b*rho
    x1 = int(x0 + 1000*(-b))
    y1 = int(y0 + 1000*(a))
    x2 = int(x0 - 1000*(-b))
    y2 = int(y0 - 1000*(a))

    cv2.line(img,(x1,y1),(x2,y2),(255,255,0),2)
'''

_, contours, hierarchy_ = \
cv2.findContours(img_close,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

#image = cv2.drawContours(img, contours, -1, (0,0,255), 2)
#
#cv2.imshow('open', img_open)
#cv2.imshow('close', img_close)
#cv2.imshow('image', img)
#img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
'''
#
#285

b,g,r = cv2.split(img)#cv2.cvtColor(img, cv2.COLOR_BGR2HSV))

hist_b = cv2.calcHist([b], [0], None, [256], [0,255])
hist_g = cv2.calcHist([g], [0], None, [256], [0,255])
hist_r = cv2.calcHist([r], [0], None, [256], [0,255])

plt.plot(hist_b)

hist_b_sample = hist_b[150:]
pos = np.linspace(150,255,106).astype(int)
peak_max = pos[np.argmax(hist_b_sample)]

boundary_left = np.array(peak_max - 20)
boundary_right = np.array(peak_max + 5)

img_b = img[:,:,0]
mask = np.zeros(img_b.shape, dtype = np.uint8)

cv2.inRange(img_b, boundary_left, boundary_right, mask)
cv2.imshow('mask', mask)
'''
#90
b,g,r = cv2.split(img)#cv2.cvtColor(img, cv2.COLOR_BGR2HSV))

hist_b = cv2.calcHist([b], [0], None, [256], [0,255])
hist_g = cv2.calcHist([g], [0], None, [256], [0,255])
hist_r = cv2.calcHist([r], [0], None, [256], [0,255])

#hist_g = hist_g/max(hist_g)*1000
plt.plot(hist_g)

pos = signal.argrelextrema(hist_g, np.greater)[0]
peak = hist_g[pos]

position = 0
start = 0
end = 255
for i in range(len(pos)):
    if 70 < pos[i] and start == 0:
        start = i
    if pos[i] > 130:
        end = i
        break
        
for i in range(start, end):
    if peak[i] > 10000 and peak[i] == np.max(peak[start: end]):
        position = pos[i]
        break
if position > 120 or position == 0:
    position = pos[np.argmax(peak)]
print(position)

boundary_left = np.array(position - 10)
boundary_right = np.array(position + 7)

img_g = img[:,:,1]
mask = np.zeros(img_g.shape, dtype = np.uint8)

cv2.inRange(img_g, boundary_left, boundary_right, mask)
cv2.imshow('mask', mask)




'''
pos = signal.argrelextrema(hist_b, np.greater)
peak = hist_b[pos]

pos_peak = np.vstack((pos[0],peak))
pos_peak = pos_peak.T[np.lexsort(pos_peak)].T
pos1 = pos_peak[0,:]
peak1 = pos_peak[1,:]

plt.scatter(pos1, peak1)
'''
#img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#threshold = 130
#ret,img_binary = cv2.threshold(img,threshold,255,cv2.THRESH_BINARY_INV)
#
#img# = cv2.cvtColor(img_binary, cv2.COLOR_HSV2BGR)
#
#
#
#cv2.imshow('img',img)