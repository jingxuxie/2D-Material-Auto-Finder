# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 11:34:21 2020

@author: HP
"""

import numpy as np
import cv2

img = cv2.imread('F:/Desktop2019.8.15/SonyView/support_file/redo_gray.png', cv2.IMREAD_UNCHANGED)
#img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

#img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGRA)

img[:,:,3] = 150
cv2.imshow('1', img)
img[np.all(img == [255,255,255,150], axis = 2)]=[255,255,255,0]

cv2.imwrite('F:/Desktop2019.8.15/SonyView/support_file/redo_gray_opacity.png',img)