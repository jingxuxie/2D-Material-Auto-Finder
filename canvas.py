# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 15:58:43 2020

@author: HP
"""

import numpy as np
import cv2
import sys
from PyQt5.QtWidgets import (QApplication, QLabel, QWidget)
'''
img1 = cv2.imread('F:/2020/1/21/01-21-2020-101.jpg')
img2 = np.zeros((512,512,3), dtype = np.uint8)

rows, cols, channels = img2.shape
roi = img1[0:rows, 0:cols]
cv2.line(img2, (100,100), (300,300), (0,0,255),5)

img2gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
ret, mask = cv2.threshold(img2gray, 10, 255, cv2.THRESH_BINARY)
mask_inv = cv2.bitwise_not(mask)

img1_bg = cv2.bitwise_and(roi,roi,mask = mask_inv)
img2_fg = cv2.bitwise_and(img2,img2,mask = mask)

dst = cv2.add(img1_bg,img2_fg)
img1[0:rows, 0:cols ] = dst

cv2.imshow('1',img1)
'''


#def calculate_angle(x11,y11,x12,y12,x21,y21,x22,y22):
#    '''
#    x11 = min(pos1_x1, pos1_x2)
#    x12 = max(pos1_x1, pos1_x2)
#
#    y11 = min(pos1_y1, pos1_y2)
#    y12 = max(pos1_y1, pos1_y2)
#    
#    x21 = min(pos2_x1, pos2_x2)
#    x22 = max(pos2_x1, pos2_x2)
#    
#    y21 = min(pos2_y1, pos2_y2)
#    y22 = max(pos2_y1, pos2_y2)
#'''
#    a_square = (x12 - x11)**2 + (y12 - y11)**2
#    b_square = (x22 - x21)**2 + (y22 - y21)**2
#    a = np.sqrt(a_square)
#    b = np.sqrt(b_square)
#    c_square = ((x12 - x11)-(x22 - x21))**2 + ((y12 - y11)-(y22 - y21))**2
#    if a*b ==0:
#        theta = 0
#    else:
#        theta = (a_square + b_square - c_square)/(2 * a * b)
#        theta = np.arccos(theta)
#        theta = theta/np.pi*180
#
#    print(a, b, c_square)
#    return theta
#
#if __name__ == '__main__':
#    img = np.zeros((512,512,3), dtype = np.uint8)
#    
#    x11,y11,x12,y12,x21,y21,x22,y22 = 100,100,200,000,100,100,200,000
#    aaa = calculate_angle(x11,y11,x12,y12,x21,y21,x22,y22)
#    
#    cv2.line(img, (x11, y11), (x12, y12), (255,0,0), 2)
#    cv2.line(img, (x21, y21), (x22, y22), (0,0,255), 2)
#    cv2.imshow('img',img)


#import sys
#from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel)
#from PyQt5.QtCore import Qt
# 
# 
#class AppDemo(QMainWindow):
# 
#    def __init__(self):
#        super().__init__()
#        self.init_ui()
# 
#    def init_ui(self):
#        self.resize(300, 200)
#        self.setWindowTitle('666')
#        self.label = QLabel(self)
#        self.label.setAlignment(Qt.AlignCenter)
#        self.label.setText('六神花露水')
#        self.label.setGeometry(5, 5, 145, 185)
#        self.label.setMouseTracking(True)
# 
#        self.label_mouse_x = QLabel(self)
#        self.label_mouse_x.setGeometry(155, 5, 80, 30)
#        self.label_mouse_x.setText('x')
#        self.label_mouse_x.setMouseTracking(True)
# 
#        self.label_mouse_y = QLabel(self)
#        self.label_mouse_y.setText('y')
#        self.label_mouse_y.setGeometry(155, 40, 80, 30)
#        #self.label_mouse_y.setMouseTracking(True)
# 
#    def mouseMoveEvent(self, event):
#        s = event.windowPos()
#        print(s)
#        self.setMouseTracking(True)
#        self.label_mouse_x.setText('X:' + str(s.x()))
#        self.label_mouse_y.setText('Y:' + str(s.y()))
# 
# 
#def run_it():
#    app = QApplication(sys.argv)
#    w = AppDemo()
#    w.show()
#    sys.exit(app.exec_())
# 
# 
#if __name__ == '__main__':
#    run_it()

'''
class MouseTracker(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setMouseTracking(True)

    def initUI(self):
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Mouse Tracker')
        self.label = QLabel(self)
        self.label.resize(200, 40)
        self.show()

    def mouseMoveEvent(self, event):
        self.label.setText('Mouse coords: ( %d : %d )' % (event.x(), event.y()))

    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MouseTracker()
    sys.exit(app.exec_())    
   ''' 

a = [1,2,3,4,5]
for i in a:
    if i == 3:
        i = 6
