# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 16:42:30 2020

@author: HP
"""

from MainWindow2_0 import MainWindow
from Camera import Camera
from PyQt5.QtWidgets import QApplication, QSplashScreen, QHBoxLayout
from PyQt5.QtCore import Qt, QDir, QUrl
from PyQt5.QtGui import QPixmap, QPalette, QColor
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QSound
import sys
import os

class LiveWindow(MainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Camera Live(v3.0)')
        
        self.button_save_as.hide()
    
        self.button_release.clicked.connect(self.edit)
        
        self.Editor = None
        self.Editor = EditWindow()
        
        palette1 = QPalette()
        palette1.setColor(palette1.Background,QColor(240,250,205))
        self.setPalette(palette1)
        self.show()
        
    def edit(self):
        if self.Editor is None or self.Editor.is_showing == False:
            self.Editor.is_showing = True
            self.Editor.show()
        self.Editor.openfile = True
        self.Editor.img_raw = self.img_release
        self.Editor.img_raw_not_cropped = self.img_release
        self.Editor.openfile_timer.start(40)
        



class EditWindow(MainWindow):
    def __init__(self):
        super().__init__()
          
        self.setWindowTitle('Camera Editor(v3.0)')
        self.button_release.hide()
        self.button_live.hide()
        self.button_saveto.hide()
        self.release_folder_lbl.hide()
        self.toolbar_search.hide()
        
        self.is_showing = False
        
        
    def closeEvent(self, event):
        self.is_showing = False

def get_folder_from_file(filename):
        folder = filename
        while folder[-1] != '/':
            folder = folder[:-1]
        return folder


if __name__ == '__main__':
    #os.environ["CUDA_VISIBLE_DEVICES"] = "1"
    app = QApplication(sys.argv)
    
    splash_path = os.path.abspath(__file__).replace('\\','/')
    splash_path = get_folder_from_file(splash_path)
    splash = QSplashScreen(QPixmap(splash_path + 'support_file/shutter.jpg'))
    splash.show()
    splash.showMessage('Loading……')
    
#    camera = Camera(0)
#    camera.initialize()
     
    live = LiveWindow()
    
    splash.close()
    sys.exit(app.exec_())
    
#    camera.close_camera()
