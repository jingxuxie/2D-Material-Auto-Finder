# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 11:44:01 2020

@author: HP
"""

import cv2
import numpy as np
import time
from matplotlib import pyplot as plt


img = cv2.imread('F:/2020/2/6/02-11-2020-1.jpg')
time_start = time.time()
i = 0
for i in range(1):
    img_temp = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imshow('img', img_temp)
    laplacian = cv2.Laplacian(img_temp,cv2.CV_64F)
    mean = np.var(laplacian)#也可直接var(img_temp)更快一些
    i += 1
plt.imshow(laplacian,cmap = 'gray')
time_end = time.time()

print(mean)
print(time_end - time_start)