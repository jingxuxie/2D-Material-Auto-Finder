# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 17:24:35 2020

@author: HP
"""
import PyQt5
import sys
#from PyQt5.QtWidgets import 
#from PyQt5.QtCore import 
#from PyQt5.QtGui import 
#
#from PyQt5.QtCore import 
import sys
import cv2
import numpy as np
import time
import sys
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QApplication

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, 
    QSizePolicy, QLabel, QFontDialog, QApplication)
import sys
import pyautogui
import win32gui

class Example(QWidget):
    
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
        
    def initUI(self):      

        vbox = QVBoxLayout()

        btn = QPushButton('Dialog', self)
        btn.setSizePolicy(QSizePolicy.Fixed,
            QSizePolicy.Fixed)
        
        btn.move(20, 20)

        vbox.addWidget(btn)

        btn.clicked.connect(self.showDialog)
        
        self.lbl = QLabel('Knowledge only matters', self)
        self.lbl.move(130, 20)

        vbox.addWidget(self.lbl)
        self.setLayout(vbox)          
        
        self.setGeometry(300, 300, 250, 180)
        self.setWindowTitle('Font dialog')
        self.show()
        
        
    def showDialog(self):

        font, ok = QFontDialog.getFont()  
        if ok:
            self.lbl.setFont(font)
        
        
if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    ret, img_1 = cap.read()
    time_start = time.time()
    gray_1 = cv2.cvtColor(img_1, cv2.COLOR_BGR2GRAY)
    time.sleep(0.02)
    ret, img_2 = cap.read()
    time_end = time.time()
    gray_2 = cv2.cvtColor(img_2, cv2.COLOR_BGR2GRAY)
    d_frame = cv2.absdiff(gray_1, gray_2)
    cv2.imshow('img_1',img_1)
    cv2.imshow('img_2',img_2)
    cv2.imshow('diff',d_frame)
    print(time_end - time_start)
    print(np.sum(d_frame[d_frame>50]))
#    window_name = 'PriorTerminal'
#    bx2_hwnd = win32gui.FindWindow(None, window_name)
#    left, top, right, bottom = win32gui.GetWindowRect(bx2_hwnd)
#    print(left, top, right, bottom)
##    time_start = time.time()
#    img = pyautogui.screenshot(region=[left+10,top,right-left-20,bottom-top-10])
#    img = cv2.cvtColor(np.asarray(img),cv2.COLOR_RGB2BGR)
#    cv2.imshow('img',img)
#    time_end = time.time()
#    print(time_end - time_start)
#    app = QApplication(sys.argv)
#    ex = Example()
#    sys.exit(app.exec_())


    '''
    playlist = QMediaPlaylist()
    url = QUrl.fromLocalFile("./shutter_sound.mp3")
    playlist.addMedia(QMediaContent(url))
    playlist.setPlaybackMode(QMediaPlaylist.Loop)
    
    player = QMediaPlayer()
    player.setPlaylist(playlist)
    player.play()
    '''

'''
import PyQt5.QtCore as C
import PyQt5.QtMultimedia as M
import sys
 
app=C.QCoreApplication(sys.argv)
 
url= C.QUrl.fromLocalFile("./shutter_sound.mp3")
content= M.QMediaContent(url)
player = M.QMediaPlayer()
player.setMedia(content)
player.play()
 
player.stateChanged.connect( app.quit )
app.exec()
'''

'''
from PyQt5.QtWidgets import (QWidget, QPushButton, QFrame, 
    QColorDialog, QApplication)
from PyQt5.QtGui import QColor
import sys
from shutil import copyfile

class Example(QWidget):
    
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
        
    def initUI(self):      

        col = QColor(0, 0, 0) 

        self.btn = QPushButton('Dialog', self)
        self.btn.move(20, 20)

        self.btn.clicked.connect(self.showDialog)

        self.frm = QFrame(self)
        self.frm.setStyleSheet("QWidget { background-color: %s }" 
            % col.name())
        self.frm.setGeometry(130, 22, 100, 100)            
        
        self.setGeometry(300, 300, 250, 180)
        self.setWindowTitle('Color dialog')
        self.show()
        
        
    def showDialog(self):
      
        col = QColorDialog.getColor()

        if col.isValid():
            self.frm.setStyleSheet("QWidget { background-color: %s }"
                % col.name())
            
import sys
from PyQt5.QtWidgets import (QWidget, QToolTip, 
    QPushButton, QApplication)
from PyQt5.QtGui import QFont 
from PyQt5.QtGui import QPixmap, QPalette, QColor
class Example1(QWidget):
    
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
        
    def initUI(self):
        
        QToolTip.setFont(QFont('SansSerif', 10))
        
        self.setToolTip('This is a <b>QWidget</b> widget')
        
        btn = QPushButton('Button', self)
        btn.setToolTip('This is a <b>QPushButton</b> widget')
        btn.resize(btn.sizeHint())
        btn.move(50, 50)       
        btn.setStyleSheet("QPushButton{border-radius:13px}"
                          "QPushButton{background-color:rgb(198,224,205)}"
                         "QPushButton{color:rgb(101,153,26)}" #按键前景色
                         "QPushButton{background-color:rgb(198,224,205)}"  #按键背景色
                         "QPushButton:hover{color:red}" #光标移动到上面后的前景色
        )                        
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Tooltips')   
        palette1 = QPalette()
        palette1.setColor(palette1.Background,QColor(198-30,224-30,205-30))
        self.setPalette(palette1)
        self.show()
        
        
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = Example1()
    sys.exit(app.exec_())
'''  
#if __name__ == '__main__':
#    
#    with open(self.current_dir+'calibration.txt','w') as f:
#                f.write(self.calibration)
    
#     with open('F:\Desktop2019.8.15\SonyView\support_file'+'\calibration.txt') as f:
#         a = f.read()
    
    
    
    
#    img = cv2.imread('H:/Jingxu/2-19/temp/02-19-2020-1-04_04-02_03.jpg')
#    rec_x1 = img.shape[1] - 300
#    rec_y1 = 100
#    rec_x2 = rec_x1 + 200
#    rec_y2 = rec_y1 + 200
#    print(rec_x1, rec_y1,rec_x2, rec_y2)
#    cv2.rectangle(img,(rec_x1,rec_y1),(rec_x2,rec_y2),(0,0,255),3)
#
#    cv2.imshow('img',img)
#    cv2.imwrite('H:/Jingxu/2-18/results/test.jpg', img)
#    '''
#    app = QApplication(sys.argv)
#    ex = Example()
#    sys.exit(app.exec_())
#    '''
#    line = [1,2,3]
#    with open('focus.txt', 'a') as f:
#        f.write(str(line)+'\n')
        
        
#    with open("focus.txt", "r") as f:
#        for line in f.readlines():
#            line = line.strip('\n')  #去掉列表中每一个元素的换行符
#            for character in line:
#                if character
    
    
    
    
    