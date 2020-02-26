# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 17:24:35 2020

@author: HP
"""
import PyQt5
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from PyQt5.QtCore import *
import sys
import cv2

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
            
        
if __name__ == '__main__':
    
    img = cv2.imread('H:/Jingxu/2-19/temp/02-19-2020-1-04_04-02_03.jpg')
    rec_x1 = img.shape[1] - 300
    rec_y1 = 100
    rec_x2 = rec_x1 + 200
    rec_y2 = rec_y1 + 200
    print(rec_x1, rec_y1,rec_x2, rec_y2)
    cv2.rectangle(img,(rec_x1,rec_y1),(rec_x2,rec_y2),(0,0,255),3)

    cv2.imshow('img',img)
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
    
    
    
    
    