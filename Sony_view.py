
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 22:38:02 2019

@author: Jingxu Xie (Best Sir Zhang)
"""
import numpy as np
from PyQt5.QtWidgets import QWidget, QSlider, QVBoxLayout, QHBoxLayout, \
    QLabel, QApplication, QGridLayout, QPushButton, QCheckBox, QAction, \
    QFileDialog, QMainWindow, QDesktopWidget, QToolButton, QComboBox,\
    QMessageBox, QProgressBar, QSplashScreen
from PyQt5.QtCore import Qt, QThread, QTimer, QObject, pyqtSignal, QBasicTimer
from PyQt5.QtGui import QPixmap, QImage, QIcon
import pyqtgraph as pg
import sys
import cv2
import os
import time
from Camera import Camera
from BresenhamAlgorithmLine import Bresenham_Algorithm as BA 
import copy
from numba import jit
from drawing import Line, Rectangle, Circle

@jit(nopython = True)
def go_fast(a,b,c):
    for i in range(a.shape[0]):
        for j in range(a.shape[1]):
            temp = int(a[i,j]+b)*c
            temp = max(0, temp)
            temp = min(temp,255)
            a[i,j] = temp
            #a[i,j] = 
            '''
            if a[i,j] > 255-b:                
                a[i,j] = 255
            elif a[i,j] > c:
                a[i,j] = 255
            else:
                a[i,j] = (a[i,j]+b)#*(255/(abs(c-b)+0.0001))
            '''
            #a[i,j] = max(0,a[i,j])
            #a[i,j] = min(255, a[i,j])
            #a[i,j] = 255
    return a

@jit(nopython = True)
def matrix_divide(a,b):
    if len(a.shape) == 3:
        for i in range(a.shape[0]):
            for j in range(a.shape[1]):
                for k in range(a.shape[2]):
                    a[i,j,k] = round(a[i,j,k]/(b+0.001))
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
    group1_x, group1_y = BA(x1_1, y1_1, x1_2, y1_2)
    group2_x, group2_y = BA(x2_1, y2_1, x2_2, y2_2)
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


class Communicate(QObject):
    
    updateBW = pyqtSignal(int)
          
class RGB_Slider(QWidget):
    
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.r_min_sld = QSlider(Qt.Horizontal,self)
        self.r_max_sld = QSlider(Qt.Horizontal,self)       
        self.g_min_sld = QSlider(Qt.Horizontal,self)
        self.g_max_sld = QSlider(Qt.Horizontal,self)        
        self.b_min_sld = QSlider(Qt.Horizontal,self)
        self.b_max_sld = QSlider(Qt.Horizontal,self)
        self.bright_sld = QSlider(Qt.Horizontal,self)
        self.contrast_sld = QSlider(Qt.Horizontal,self)
        
        bright_range = [-200, 200]
        contr_range = [0, 150]
        self.r_min_sld.setRange(*bright_range)
        self.r_max_sld.setRange(*contr_range)       
        self.g_min_sld.setRange(*bright_range)
        self.g_max_sld.setRange(*contr_range)
        self.b_min_sld.setRange(*bright_range)
        self.b_max_sld.setRange(*contr_range)
        self.bright_sld.setRange(*bright_range)
        self.contrast_sld.setRange(*contr_range)
        
        
        self.r_min_lbl = QLabel()
        self.r_max_lbl = QLabel()        
        self.g_min_lbl = QLabel()
        self.g_max_lbl = QLabel()       
        self.b_min_lbl = QLabel()
        self.b_max_lbl = QLabel()
        self.bright_lbl = QLabel()
        self.contrast_lbl = QLabel()
        
        
        self.r_min_lbl.setText('R_bri')
        self.r_max_lbl.setText('R_contr')      
        self.g_min_lbl.setText('G_bri')
        self.g_max_lbl.setText('G_contr')       
        self.b_min_lbl.setText('B_bri')
        self.b_max_lbl.setText('B_contr')
        self.bright_lbl.setText('Bright')
        self.contrast_lbl.setText('Contrast')

        
        self.grid = QGridLayout()
        self.grid.addWidget(self.bright_lbl, *[1,0])
        self.grid.addWidget(self.bright_sld, *[1,1])
        
        self.grid.addWidget(self.contrast_lbl, *[2,0])
        self.grid.addWidget(self.contrast_sld, *[2,1])
        
        self.grid.addWidget(self.r_min_lbl, *[3,0])
        self.grid.addWidget(self.r_min_sld, *[3,1])
        
        self.grid.addWidget(self.r_max_lbl, *[4,0])
        self.grid.addWidget(self.r_max_sld, *[4,1])
        
        self.grid.addWidget(self.g_min_lbl, *[5,0])
        self.grid.addWidget(self.g_min_sld, *[5,1])
        
        self.grid.addWidget(self.g_max_lbl, *[6,0])
        self.grid.addWidget(self.g_max_sld, *[6,1])
        
        self.grid.addWidget(self.b_min_lbl, *[7,0])
        self.grid.addWidget(self.b_min_sld, *[7,1])
        
        self.grid.addWidget(self.b_max_lbl, *[8,0])
        self.grid.addWidget(self.b_max_sld, *[8,1])
                
        
class ProgressBar(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.pbar = QProgressBar(self)
        self.pbar.setGeometry(30, 40, 350, 25)

        self.timer = QBasicTimer()
        self.timer.start(50, self)
        self.progress = 0
        self.center()
        self.setWindowTitle('Capturing background...')    
        
    def timerEvent(self,e):
        self.pbar.setValue(self.progress)
    
    def center(self):
      qr = self.frameGeometry()
      cp = QDesktopWidget().availableGeometry().center()
      qr.moveCenter(cp)
      self.move(qr.topLeft())



class MainWindow(QMainWindow):
    
    def __init__(self,camera = None):
        super().__init__()
        self.camera = camera
        
        self.openfile = False
        #self.open_img = 
        self.initUI()
    
    def initUI(self):
        #self.file_dir_test()
        self.current_dir = os.path.abspath(__file__).replace('\\','/')
        self.current_dir = self.get_folder_from_file(self.current_dir)
        self.current_dir = self.current_dir+'support_file/'
        self.gray = False
        self.img_raw = cv2.imread(self.current_dir+'no_camera.png')
        self.img_show = cv2.imread(self.current_dir+'no_camera.png')
        if self.img_show is None:
            self.img_show = np.zeros((512,512,3), np.uint8)
            self.img_raw = np.zeros((512,512,3), np.uint8)
            QMessageBox.critical(self, "Missing file", 'The no_camera.png file '
                                 'is not found. Please check support_file')
        self.bk_filename = self.current_dir+'backgroundx5.png'
        self.background_norm = np.zeros(3)
        self.bk_error = False
        self.get_bk_normalization()
        try:
            with open(self.current_dir+'saveto.txt') as f:
                self.save_folder = f.read()
        except:
            self.save_folder = 'C:/'
            QMessageBox.critical(self, "Missing file", 'The supporting saveto.txt '
                                  'file is missing. Path not set')
        self.date = time.strftime("%m-%d-%Y")
        self.release_count = 1
        
        self.selectbk_folder = 'C:/'
        self.showFileDialog_folder = 'C:/'
        self.saveFileDialog_folder = 'C:/'
        
        self.calibrition = 14.55
         
        openBK = QAction('Select BK', self)
        openBK.triggered.connect(self.select_background)
        
        openFile = QAction('Open file', self)
        openFile.triggered.connect(self.showFileDialog)
        
        saveFile = QAction('Save as', self)
        saveFile.triggered.connect(self.saveFileDialog)
        
        capture_BK = QAction('Capture BK', self)
        capture_BK.triggered.connect(self.capture_background)
        
        restart = QAction('Restart', self)
        restart.triggered.connect(self.restart_program)
        
        help_contact = QAction('Contact', self)
        help_contact.triggered.connect(self.contact)
        
        help_about = QAction('About', self)
        help_about.triggered.connect(self.about)
        
        #acknowledge = QAction('Acknowledgement', self)
        #acknowledge.triggered.connect(self.acknowledgement)
        
        self.menubar = self.menuBar()
        fileMenu = self.menubar.addMenu('&File')
        fileMenu.addAction(openBK)
        fileMenu.addAction(openFile)
        fileMenu.addAction(saveFile)
        
        toolMenu = self.menubar.addMenu('&Tools')
        toolMenu.addAction(capture_BK)
        toolMenu.addAction(restart)
        
        
        HelpMenu = self.menubar.addMenu('Help')
        HelpMenu.addAction(help_contact)
        HelpMenu.addAction(help_about)
        #HelpMenu.addAction(acknowledge)

        initial_size = QAction('Home',self)
        initial_size.triggered.connect(self.initial_size)
        
        self.zoom_in_button = QToolButton()
        self.zoom_in_button.setIcon(QIcon(self.current_dir+'zoom_in.png'))
        self.zoom_in_button.setToolTip('zoom in')
        self.zoom_in_button.clicked.connect(self.zoom_in)
        self.zoom_in_button.setCheckable(True)
        #self.zoom_in_button.setChecked(False)
        #self.zoom_in_button.setText("zoom in")
        self.zoom_draw = False
        self.zoom_draw_start = False
        self.zoomed = False
        
        self.draw_shape_list = []
        self.draw_shape_list_for_redo = []
        
        self.straight_line_button = QToolButton()
        self.straight_line_button.setIcon(QIcon(self.current_dir+'straight_line.png'))
        self.straight_line_button.setToolTip('draw straight line')
        self.straight_line_button.clicked.connect(self.draw_straight_line)
        self.straight_line_button.setCheckable(True)
        self.draw_shape_line = False
        self.drawing_shape_line = False
        self.draw_shape = False
        
        self.rectangle_button = QToolButton()
        self.rectangle_button.setIcon(QIcon(self.current_dir+'square.png'))
        self.rectangle_button.setToolTip('draw rectangle')
        self.rectangle_button.clicked.connect(self.draw_rectangle)
        self.rectangle_button.setCheckable(True)
        self.draw_shape_rectangle = False
        self.drawing_shape_rectangle = False
        
        self.circle_button = QToolButton()
        self.circle_button.setIcon(QIcon(self.current_dir+'circle.png'))
        self.circle_button.setToolTip('draw circle')
        self.circle_button.clicked.connect(self.draw_circle)
        self.circle_button.setCheckable(True)
        self.draw_shape_circle = False
        self.drawing_shape_circle = False
        
        self.eraser_button = QToolButton()
        self.eraser_button.setIcon(QIcon(self.current_dir+'eraser.png'))
        self.eraser_button.setToolTip('eraser')
        
        
        self.undo_draw_button = QToolButton()
        self.undo_draw_button.setIcon(QIcon(self.current_dir+'undo_gray.png'))
        self.undo_draw_button.setToolTip('undo')
        self.undo_draw_button.clicked.connect(self.undo_draw)
        self.undo_draw_button.setShortcut('Ctrl+Z')
        
        self.redo_draw_button = QToolButton()
        self.redo_draw_button.setIcon(QIcon(self.current_dir+'redo_gray.png'))
        self.redo_draw_button.setToolTip('redo')
        self.redo_draw_button.clicked.connect(self.redo_draw)
        self.redo_draw_button.setShortcut('Ctrl+Y')
        
        self.clear_draw_button = QToolButton()
        self.clear_draw_button.setIcon(QIcon(self.current_dir+'clear.png'))
        self.clear_draw_button.setToolTip('clear drawing')
        self.clear_draw_button.clicked.connect(self.clear_draw)
        
        self.angle_button = QToolButton()
        self.angle_button.setIcon(QIcon(self.current_dir+'angle_measurement.png'))
        self.angle_button.setToolTip('measure angle')
        self.angle_button.clicked.connect(self.angle_measuremnet)
        
        self.graphene_button = QToolButton()
        self.graphene_button.setIcon(QIcon(self.current_dir+'graphene.png'))
        self.graphene_button.setToolTip('graphene auto detection')
        self.graphene_button.clicked.connect(self.graphene_hunt)
        
        self.toolbar1 = self.addToolBar('zoom')
        #self.toolbar.addAction(initial_size)
        self.toolbar1.addWidget(self.zoom_in_button)
        
        self.toolbar2 = self.addToolBar('drawing')
        self.toolbar2.addWidget(self.straight_line_button)
        self.toolbar2.addWidget(self.rectangle_button)
        self.toolbar2.addWidget(self.circle_button)
        self.toolbar2.addWidget(self.eraser_button)
        self.toolbar2.addWidget(self.undo_draw_button)
        self.toolbar2.addWidget(self.redo_draw_button)
        self.toolbar2.addWidget(self.clear_draw_button)
        
        self.toolbar3 = self.addToolBar('advanced tools')
        self.toolbar3.addWidget(self.angle_button)
        self.toolbar3.addWidget(self.graphene_button)
        
        self.toolbar = self.addToolBar(' ')

        self.sld = RGB_Slider()
        self.rgb_initialize()
        self.sld_connect()
                        
        self.button_release = QPushButton('Release', self)
        self.button_release.clicked.connect(self.update_release)
        #self.button_release.setCheckable(True)
        
        self.button_live = QPushButton('Live View', self)
        self.button_live.clicked.connect(self.start_live)
        self.button_live.setCheckable(True)
        
        button_reset_contrast = QPushButton('Reset Contrast', self)
        button_reset_contrast.clicked.connect(self.rgb_initialize)
        
        button_saveto = QPushButton('Save path', self)
        button_saveto.setToolTip('This is the folder where your released files will be saved')
        button_saveto.clicked.connect(self.save_path_setting)
        
        self.save_folder_lbl = QLabel(self)
        if len(self.save_folder) > 20:
            self.save_folder_lbl.setText('...'+self.save_folder[-25:])
        else:
            self.save_folder_lbl.setText(self.save_folder)
        
        self.live_count = 0

        cb_gray = QCheckBox('Gray',self)
        cb_gray.setChecked(True)
        cb_gray.toggle()
        cb_gray.stateChanged.connect(self.is_gray)
        self.gray = False
        
        cb_sb = QCheckBox('Divide BK',self)
        cb_sb.setChecked(True)
        cb_sb.toggle()
        cb_sb.stateChanged.connect(self.is_SB)
        self.SB = False
        
        self.combo_mag = QComboBox(self)
        self.combo_mag.addItem('5x')
        self.combo_mag.addItem('10x')
        self.combo_mag.addItem('20x')
        self.combo_mag.addItem('50x')
        self.combo_mag.addItem('100x')
        self.combo_mag.activated[str].connect(self.set_magnification)
        self.magnification = int(self.combo_mag.currentText()[:-1])

        
        self.cb_crop = QCheckBox('Crop', self)
        self.cb_crop.setChecked(True)
        self.cb_crop.toggle()
        self.cb_crop.stateChanged.connect(self.is_Crop)
        self.CP = False
        
        self.cb_tool_distance = QCheckBox('Distance', self) 
        self.cb_tool_distance.setChecked(True)
        self.cb_tool_distance.toggle()
        self.cb_tool_distance.stateChanged.connect(self.is_distance)
        self.DT = False
        self.DT_draw = False
        
        self.distance_lbl = QLabel(self)
        self.distance = 0.
        self.distance_lbl.setText(str(round(self.distance,2))+' um')
        
        self.cb_tool_contrast = QCheckBox('Contrast', self)
        self.cb_tool_contrast.setChecked(True)
        self.cb_tool_contrast.toggle()
        self.cb_tool_contrast.stateChanged.connect(self.is_contrast)
        self.CT = False
        self.CT_draw = False
        
        self.contrast_lbl = QLabel(self)
        self.contrast = 0.
        self.contrast_lbl.setText(str(round(self.contrast,2)))

        self.pixmap = QPixmap()
        
        self.lbl_main = QLabel(self)
        self.lbl_main.setAlignment(Qt.AlignCenter)
        self.lbl_main.setPixmap(self.pixmap)
        
        self.pw_hist = pg.PlotWidget()
        self.pw_hist.setFixedHeight(300)
        #self.lbl.resize(1920*0.8,1080*0.8)
        
        
        hbox_button = QHBoxLayout()
        hbox_button.addWidget(self.button_release)
        hbox_button.addWidget(self.button_live)
        hbox_button.addWidget(cb_gray)
        hbox_button.addWidget(cb_sb)
        hbox_button.addWidget(self.cb_crop)
        
        vbox_l = QVBoxLayout()
        vbox_l.addWidget(self.lbl_main)
        vbox_l.addLayout(hbox_button)
        
        hbox_distance = QHBoxLayout()
        hbox_distance.addWidget(self.cb_tool_distance)
        hbox_distance.addWidget(self.distance_lbl)
        
        hbox_contrast = QHBoxLayout()
        hbox_contrast.addWidget(self.cb_tool_contrast)
        hbox_contrast.addWidget(self.contrast_lbl)
        
        vbox_r = QVBoxLayout()
        vbox_r.addWidget(self.combo_mag, Qt.AlignCenter)
        vbox_r.addStretch(1)
        vbox_r.addLayout(hbox_distance)
        vbox_r.addStretch(0.5)
        vbox_r.addLayout(hbox_contrast)
        vbox_r.addStretch(1)
        vbox_r.addWidget(self.pw_hist)
        vbox_r.addStretch(1)
        vbox_r.addLayout(self.sld.grid)
        #vbox_r.addStretch(1)
        vbox_r.addWidget(button_reset_contrast)
        vbox_r.addStretch(2)
        vbox_r.addWidget(button_saveto, Qt.AlignBottom)
        #vbox_r.addStretch(1)
        vbox_r.addWidget(self.save_folder_lbl)
        vbox_r.addStretch(1)
        
        
        hbox = QHBoxLayout()
        hbox.addLayout(vbox_l)
        hbox.addLayout(vbox_r)
        
        self.central_widget = QWidget()
       
        self.layout = QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)
        self.layout.addLayout(hbox)
        
        self.live_timer = QTimer()
        self.openfile_timer = QTimer()
        self.restart_timer = QTimer()
        self.capture_bk_timer = QTimer()
        
        #self.restart_timer.start(5000)
        #self.restart_timer.timeout.connect(self.auto_restart)
        
        self.live_timer.timeout.connect(self.update_live)
        self.openfile_timer.timeout.connect(self.refresh_show)
        self.openfile_timer.timeout.connect(self.show_on_screen)
        self.capture_bk_timer.timeout.connect(self.capture_bk_start)
        
        desktop = QDesktopWidget()
        self.screen_width = desktop.screenGeometry().width()
        self.screen_height = desktop.screenGeometry().height()

        self.initial_window_width = self.screen_width*0.5
        self.initial_window_height = self.screen_height*0.7
        self.resize(self.initial_window_width, self.initial_window_height)
        self.setWindowTitle('Sony Remote (v1.0)')
        self.setWindowIcon(QIcon(self.current_dir+'Sony.png'))
        #self.setObjectName('MainWindow')
        #self.setStyleSheet('#MainWindow{background-color: black}')
        
        self.show()
   
    def undo_redo_setting(self):
        self.undo_draw_button.setIcon(QIcon(self.current_dir+'undo.png'))
        self.draw_shape_list_for_redo = []
        self.redo_draw_button.setIcon(QIcon(self.current_dir+'redo_gray.png'))    

    def undo_draw(self):
        if len(self.draw_shape_list) > 0:
            self.draw_shape_list_for_redo.append(self.draw_shape_list[-1])
            self.redo_draw_button.setIcon(QIcon(self.current_dir+'redo.png'))
            self.draw_shape_list.pop()
            if len(self.draw_shape_list) == 0:
                self.undo_draw_button.setIcon(QIcon(self.current_dir+'undo_gray.png'))

    def redo_draw(self):
        if len(self.draw_shape_list_for_redo) > 0:
            self.draw_shape_list.append(self.draw_shape_list_for_redo[-1])
            self.undo_draw_button.setIcon(QIcon(self.current_dir+'undo.png'))
            self.draw_shape_list_for_redo.pop()
            if len(self.draw_shape_list_for_redo) == 0:
                self.redo_draw_button.setIcon(QIcon(self.current_dir+'redo_gray.png'))
    
    def clear_draw(self):
        reply = QMessageBox.warning(self, "warning", 'Do you want to clear all '+\
                                        'the drawing? Attention, this action ' +\
                                        'is irreversible!',\
                                    QMessageBox.No | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            self.draw_shape_initial()
            self.draw_shape_list = []
            self.draw_shape_list_for_redo = []
            self.undo_draw_button.setIcon(QIcon(self.current_dir+'undo_gray.png'))
            self.redo_draw_button.setIcon(QIcon(self.current_dir+'redo_gray.png'))

    
    def draw_shape_initial(self):
        self.straight_line_button.setChecked(False)
        self.draw_shape_line = False
        self.drawing_shape_line = False
        
        self.rectangle_button.setChecked(False)
        self.draw_shape_rectangle = False
        self.drawing_shape_rectangle = False
        
        self.circle_button.setChecked(False)
        self.draw_shape_circle = False
        self.drawing_shape_circle = False
        #self.draw_shape = False

    def draw_straight_line(self):
        if self.straight_line_button.isChecked():
            self.tool_initial()
            self.draw_shape_line = True
            self.straight_line_button.setChecked(True)
        else:
            self.draw_shape_line = False
            self.drawing_shape_line = False
            self.straight_line_button.setChecked(False)
        #QMessageBox.information(self, 'Developing...','Draw straight line '+\
          #                      'function is developing... ')
        
    def draw_rectangle(self):
        if self.rectangle_button.isChecked():
            self.tool_initial()
            self.draw_shape_rectangle = True
            self.rectangle_button.setChecked(True)
        else:
            self.draw_shape_rectangle = False
            self.rectangle_button.setChecked(False)
        #QMessageBox.information(self, 'Developing...','Draw rectangle function '+\
         #                       'is developing... ')
        
    def draw_circle(self):
        if self.circle_button.isChecked():
            self.tool_initial()
            self.draw_shape_circle = True
            self.circle_button.setChecked(True)
        else:
            self.draw_shape_circle = False
            self.circle_button.setChecked(False)
        pass
    
    def angle_measuremnet(self):
        QMessageBox.information(self, 'Developing...','Angle measurement function '+\
                                'is developing... ')
    def graphene_hunt(self):
        QMessageBox.information(self, 'Developing...','Graphene auto test '+\
                                'function is developing... ')
    
    def get_bk_normalization(self):
        temp = cv2.imread(self.bk_filename)
        if temp is None:
            QMessageBox.critical(self, 'Error!','Missing background files, background '+\
                                 'set wrongly!')
            self.bk_error = True
        #self.background = cv2.cvtColor(self.background,cv2.COLOR_BGR2RGB)
        else:
            
            self.background = temp #cv2.cvtColor(temp,cv2.COLOR_BGR2RGB)
            for i in range(3):
                self.background_norm[i] = np.mean(self.background[:,:,i])
    
    def capture_background(self):
        reply = QMessageBox.warning(self, "Warning", 'Capture background may use '+\
                'a lot of computer memory and cause unexpected error. Please do NOT '+\
                'take any other actions during capturing. Do you want to capture?',\
                QMessageBox.No | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            self.capture_num = 0
            self.progress_bar = ProgressBar()
            self.progress_bar.show()
            self.capture_bk_timer.start(40)
            self.capture_bk_frame = []
        
    
    def capture_bk_start(self):
        if self.capture_num == 100:
            self.capture_bk_timer.stop()
            try:
                self.capture_bk_average = self.capture_bk_frame[0].astype(np.int16)
            except:
                self.progress_bar.close()
                reply = QMessageBox.critical(self, "Merroy error", 'There is an error '+\
                                          'occured when trying to capture background '+\
                                          'Do you want to retry?',\
                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if reply == QMessageBox.Yes:
                    self.capture_bk_start()
                else:
                    QMessageBox.critical(self, 'Error!','Capture background failed! '+\
                                'Please restart the program and retry or contact '+\
                                'jingxuxie@berkeley.edu for help.')
            else:
                for i in range(1, len(self.capture_bk_frame)):
                    self.capture_bk_average += self.capture_bk_frame[i]
                self.capture_bk_average = matrix_divide(self.capture_bk_average, len(self.capture_bk_frame))
                self.capture_bk_average = float2uint8(self.capture_bk_average)
                self.progress_bar.close()
                bk_savename = QFileDialog.getSaveFileName(self,'save bk',\
                                            self.current_dir,\
                                            "Image files(*.jpg *.png)")
                if bk_savename[0]:
                    cv2.imwrite(bk_savename[0], self.capture_bk_average)
        self.capture_bk_frame.append(self.img_raw)
        self.capture_num += 1
        self.progress_bar.progress = self.capture_num
        
    
    def contact(self):
        QMessageBox.information(self, 'contact','Please contact jingxuxie@berkeley.edu '+\
                                'to report bugs and support improvement advice. Thank!')
    
    def about(self):
        QMessageBox.information(self, 'About Sony Remote', 'Sony Remote v1.0. '+ \
                                'Designed and created by Jingxu Xie(谢京旭).')
        
    def acknowledgement(self):
        QMessageBox.information(self, 'acknowledgement', 'I thank a lot for Sasha\'s help.')
        
    def auto_restart(self):
        if self.camera.camera_error:
            reply = QMessageBox.warning(self, "warning", 'Failed get frame from '+\
                                        'camera. Do you want to restart?',\
                                    QMessageBox.No | QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                restart()
                self.camera.camera_error = False

    
    def restart_program(self):
        reply = QMessageBox.warning(self, "warning", "Do you want to restart?",\
                                    QMessageBox.No | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            restart()

    
    def file_dir_test(self):
        self.date = time.strftime("%m-%d-%Y")
        self.save_image_path = 'F:/'+self.date
        if not os.path.exists(self.save_image_path):
            os.makedirs(self.save_image_path)
        self.release_count = 1
    
    def initial_size(self):
        self.live_timer.stop()
        self.showNormal()

        self.window_width = self.initial_window_width
        self.window_height = self.initial_window_height
        self.img_show_resize()
        self.show_on_screen()
        
        
        #self.setFixedWidth(self.initial_window_width)
        #self.setFixedHeight(self.initial_window_height)
        self.resize(self.initial_window_width, self.initial_window_height)
        self.live_timer.start(40)
    
    def save_path_setting(self):
        fname = []
        fname = QFileDialog.getExistingDirectory(self, 'Set saving folder', self.save_folder)
        if len(fname) != 0:
            try:
                with open(self.current_dir+'saveto.txt','w') as f:
                    f.write(fname)
            except:
                QMessageBox.critical(self, "Missing file", 'The supporting saveto.txt '
                                  'file is missing. Path not set')
            else:
                self.save_folder = fname
                if len(self.save_folder) > 20:
                    self.save_folder_lbl.setText('...'+self.save_folder[-20:])
                else:
                    self.save_folder_lbl.setText(self.save_folder)
    
    def set_magnification(self, text):
        
        self.magnification = int(text[:-1])
        if self.CP:
            self.bk_filename = self.current_dir+'background_crop_x'+\
                                     str(self.magnification)+'.png'
        else:
            self.bk_filename = self.current_dir+'backgroundx'+\
                                     str(self.magnification)+'.png'
        self.get_bk_normalization()
        #self.tool_initial()
        #print(self.magnification)
        pass
   
    
    def is_contrast(self,state):
        if state == Qt.Checked:
            self.tool_initial()
            self.cb_tool_contrast.setChecked(True)
            self.CT = True
        else:
            self.CT = False
            self.CT_draw = False
            pass
    
    
    def is_distance(self,state):
        if state == Qt.Checked:
            self.tool_initial()
            self.cb_tool_distance.setChecked(True)
            #self.DT_pos_initial()
            #self.DT_draw = True
            self.DT = True
        else:
            self.DT = False
            self.DT_draw = False
    

    
    def tool_initial(self):
        self.zoom_in_button.setChecked(False)
        self.zoom_draw = False
        '''
        self.straight_line_button.setChecked(False)
        self.line_draw = False

        self.rectangle_button.setChecked(False)
        self.rectangle_draw = False
'''
        self.cb_tool_distance.setChecked(False)
        self.DT_draw = False

        self.cb_tool_contrast.setChecked(False)
        self.CT_draw = False

        self.contrast_line = []
        self.initial_measurement()
        
        self.straight_line_button.setChecked(False)
        self.draw_shape_line = False
        self.drawing_shape_line = False
        
        self.rectangle_button.setChecked(False)
        self.draw_shape_rectangle = False
        self.drawing_shape_rectangle = False
        
        self.circle_button.setChecked(False)
        self.draw_shape_circle = False
        self.drawing_shape_circle = False
        
    def initial_measurement(self):
        self.distance = 0.
        self.distance_lbl.setText(str(round(self.distance, 2))+' um')
        self.contrast = 0.
        self.contrast_lbl.setText(str(round(self.contrast, 2)))
        
    def zoom_in(self):
        if self.zoom_in_button.isChecked():
            self.tool_initial()
            self.zoom_in_button.setChecked(True)
            self.zoom_draw = True
            if not self.zoomed:
                self.zoom_draw_able = True
        else:
            self.zoom_draw = False
            self.zoom_in_button.setChecked(False)

        
    def mouse_pos_initial(self):
        self.mouse_x1, self.mouse_y1 = 0,0
        self.mouse_x2, self.mouse_y2 = 0,0
        
    
    def mousePressEvent(self, event):
        if not self.combo_mag.underMouse():    
            self.mouse_x1 = max(0, event.pos().x())
            self.mouse_y1 = max(0, event.pos().y())
            self.mouse_x2 = self.mouse_x1 
            self.mouse_y2 = self.mouse_y1
        
        if event.buttons() == Qt.LeftButton and self.zoom_draw and self.zoom_draw_able:
            self.mouse_pos_correct_rec()
            self.zoom_draw_start = True
                
        elif event.buttons() == Qt.LeftButton and self.DT:
            self.mouse_pos_correct_line()
            self.DT_draw = True
            
        elif event.buttons() == Qt.LeftButton and self.CT:
            self.mouse_pos_correct_line()
            self.line_num = len(self.contrast_line)
            if len(self.contrast_line)<2:
                self.contrast_line.append([[self.mouse_line_x1, self.mouse_line_y1]])
                self.contrast_line[self.line_num].append([self.mouse_line_x2, self.mouse_line_y2])
                
            else:
                self.contrast_line=[]
                self.contrast_line.append([[self.mouse_line_x1, self.mouse_line_y1]])
                self.contrast_line[0].append([self.mouse_line_x2, self.mouse_line_y2])
                self.line_num = 0
            self.CT_draw = True
            pass
        
        elif event.buttons() == Qt.LeftButton and self.draw_shape_line:
            self.mouse_pos_correct_line()
            self.draw_shape_list.append(Line(self.mouse_line_x1, self.mouse_line_y1, \
                                             self.mouse_line_x2, self.mouse_line_y2))
            self.drawing_shape_line = True
            self.undo_redo_setting()
        
        elif event.buttons() == Qt.LeftButton and self.draw_shape_rectangle:
            self.mouse_pos_correct_line()
            self.draw_shape_list.append(Rectangle(self.mouse_line_x1, self.mouse_line_y1,\
                                                  self.mouse_line_x2, self.mouse_line_y2))
            self.drawing_shape_rectangle = True
            self.undo_redo_setting()
            
        elif event.buttons() == Qt.LeftButton and self.draw_shape_circle:
            self.mouse_pos_correct_line()
            radius = np.sqrt((self.mouse_line_x2 - self.mouse_line_x1)**2 + \
                             (self.mouse_line_y2 - self.mouse_line_y1)**2)
            radius = round(radius/2).astype(int)
            center_x = round((self.mouse_line_x1 + self.mouse_line_x2)/2)
            center_y = round((self.mouse_line_y1 + self.mouse_line_y2)/2)
            self.draw_shape_list.append(Circle(center_x, center_y,radius))
            self.drawing_shape_circle = True
            self.undo_redo_setting()
        
        elif event.buttons() == Qt.RightButton:
            if self.zoomed:
                self.tool_initial()
                self.zoom_draw = True
                self.zoom_in_button.setChecked(True)
                self.zoomed = False
                self.zoom_draw_able = True
    
    def mouseMoveEvent(self, event):
        if not self.combo_mag.underMouse():
            self.mouse_x2 = max(0, event.pos().x())
            self.mouse_y2 = max(0, event.pos().y())
        
        if self.zoom_draw and self.zoom_draw_able:
            self.mouse_pos_correct_rec()
            
        if self.DT_draw:        
            self.mouse_pos_correct_line()
        
        if self.CT_draw:
            self.mouse_pos_correct_line()
            self.contrast_line[self.line_num][1][0] = self.mouse_line_x2
            self.contrast_line[self.line_num][1][1] = self.mouse_line_y2
        
        if self.drawing_shape_line:
            self.mouse_pos_correct_line()
            self.draw_shape_list[-1].x2 = self.mouse_line_x2
            self.draw_shape_list[-1].y2 = self.mouse_line_y2
            self.draw_shape_list[-1].pos_refresh()
            
        if self.drawing_shape_rectangle:
            self.mouse_pos_correct_line()
            self.draw_shape_list[-1].x2 = self.mouse_line_x2
            self.draw_shape_list[-1].y2 = self.mouse_line_y2
            self.draw_shape_list[-1].pos_refresh()
            
        if self.drawing_shape_circle:
            self.mouse_pos_correct_line()
            self.draw_shape_list[-1].center_x = round((self.mouse_line_x1 + \
                                                self.mouse_line_x2)/2)
            self.draw_shape_list[-1].center_y = round((self.mouse_line_y1 + \
                                                self.mouse_line_y2)/2)
            self.draw_shape_list[-1].pos_refresh()
            radius = np.sqrt((self.mouse_line_x2 - self.mouse_line_x1)**2 + \
                             (self.mouse_line_y2 - self.mouse_line_y1)**2)
            self.draw_shape_list[-1].radius = round(radius/2).astype(int)
    def mouseReleaseEvent(self, event):

        #self.mouse_x2 = max(0, event.pos().x())
        #self.mouse_y2 = max(0, event.pos().y())
           
        if event.button() == Qt.LeftButton and self.zoom_draw and self.zoom_draw_able:
            self.zoom_draw_start = False
            is_zoomed = self.mouse_pos_correct_rec()
            if is_zoomed:
                self.zoomed = True
                self.zoom_draw_able = False
            else: 
                self.zoomed = False
                self.zoom_draw_able = True
        elif event.button() == Qt.LeftButton and self.DT:    
            pass
            #self.mouse_pos_correct_line()


    def mouse_pos_correct_line(self):
        self.img_bfDT_width = self.img_show.shape[1]
        self.img_bfDT_height = self.img_show.shape[0]
            
        self.mouse_line_x1, self.mouse_line_x2, \
        self.mouse_line_y1, self.mouse_line_y2 \
        = self.mouse_pos_correct((self.mouse_x1), (self.mouse_x2), \
                                 (self.mouse_y1), (self.mouse_y2))
        if self.mouse_line_x1 >= self.img_bfDT_width:
            self.mouse_line_x1 = self.img_bfDT_width
            
        if self.mouse_line_x2 >= self.img_bfDT_width:
            self.mouse_line_x2 = self.img_bfDT_width
            
        if self.mouse_line_y1 >= self.img_bfDT_height:
            self.mouse_line_y1 = self.img_bfDT_height
            
        if self.mouse_line_y2 >= self.img_bfDT_height:
            self.mouse_line_y2 = self.img_bfDT_height
        
    def mouse_pos_correct_rec(self):
        
        self.mouse_temp_x1 = np.min([self.mouse_x1, self.mouse_x2])
        self.mouse_temp_x2 = np.max([self.mouse_x1, self.mouse_x2])
        self.mouse_temp_y1 = np.min([self.mouse_y1, self.mouse_y2])
        self.mouse_temp_y2 = np.max([self.mouse_y1, self.mouse_y2])
        
        self.img_bfzoom_width = self.img_show.shape[1]
        self.img_bfzoom_height = self.img_show.shape[0]
        
        self.img_atmouse_width = self.img_bfzoom_width
        self.img_atmouse_height = self.img_bfzoom_height
        
        
        self.mouse_rec_x1, self.mouse_rec_x2, \
        self.mouse_rec_y1, self.mouse_rec_y2 \
        = self.mouse_pos_correct((self.mouse_temp_x1), (self.mouse_temp_x2), \
                                 (self.mouse_temp_y1), (self.mouse_temp_y2))
        
        if self.mouse_rec_x1 == self.mouse_rec_x2 or self.mouse_rec_y1 == self.mouse_rec_y2 \
        or self.mouse_rec_x1 >= self.img_atmouse_width or self.mouse_rec_y1 >= self.img_atmouse_height:
            self.mouse_rec_x1, self.mouse_rec_y1 = 0, 0
            self.mouse_rec_x2, self.mouse_rec_y2 = self.img_atmouse_width, self.img_atmouse_height
            return False      
        return True
    
    def mouse_pos_correct(self, x1, x2, y1, y2):
        lbl_main_x = self.lbl_main.pos().x()
        lbl_main_y = self.lbl_main.pos().y() + self.menubar.height() + self.toolbar.height()
        lbl_main_width = self.lbl_main.frameGeometry().width()
        lbl_main_height = self.lbl_main.frameGeometry().height()
        
        img_for_mouse_correct_width = self.img_show.shape[1]
        img_for_mouse_correct_height = self.img_show.shape[0]
        
        x1 -= int(lbl_main_x + lbl_main_width/2 - img_for_mouse_correct_width/2)
        x2 -= int(lbl_main_x + lbl_main_width/2 - img_for_mouse_correct_width/2)
        y1 -= int(lbl_main_y + lbl_main_height/2 - img_for_mouse_correct_height/2)
        y2 -= int(lbl_main_y + lbl_main_height/2 - img_for_mouse_correct_height/2)
        
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = max(0, x2)
        y2 = max(0, y2)
        
        return copy.copy(x1), copy.copy(x2), copy.copy(y1), copy.copy(y2)
    
    def is_Crop(self, state):
        if not self.zoomed:
            if state == Qt.Checked:
                self.CP = True
                self.bk_filename = self.current_dir+'background_crop_x'+\
                                     str(self.magnification)+'.png'
            else:
                self.CP = False 
                self.bk_filename = self.current_dir+'backgroundx'+\
                                     str(self.magnification)+'.png'
            
            self.get_bk_normalization()
        else:
            QMessageBox.information(self, 'Crop failed','You must exit '+\
                                'zoom-in mode before cropping. Click right '+\
                                'button and click zoom-in icon in toolbar to exit')
    
    def is_SB(self, state):
        if state == Qt.Checked:
            self.SB = True
            if self.bk_error:
                self.SB = False
                QMessageBox.critical(self,'Error!','Background file not found. Check '+\
                                 'the support_file for missing background files')
        else:
            self.SB = False 
        
        
    def is_gray(self, state):
        if state == Qt.Checked:
            self.gray = True
        else:
            self.gray = False
    
    def select_background(self):
        self.live_timer.stop()
        self.openfile = True
        self.fname = QFileDialog.getOpenFileName(self, 'Select BK', \
                                                 self.selectbk_folder,\
                                                 "Image files(*.jpg *.png)")
        
        if self.fname[0]:
            self.SB = False
            #self.rgb_initialize()
            self.background = cv2.imread(self.fname[0])
            self.bk_filename = self.fname[0]
            self.get_bk_normalization()
            self.selectbk_folder = self.get_folder_from_file(self.fname[0])
            self.button_release.setChecked(False)
            self.button_live.setChecked(False)

            self.img_raw = self.background.copy()
            self.img_raw_not_cropped = self.img_raw
            self.openfile_timer.start(40)

    def set_r_min_value(self ,value):
        self.r_min = value

    def set_r_max_value(self ,value):
        self.r_max = value/10  
    
    def set_g_min_value(self ,value):
        self.g_min = value
        
    def set_g_max_value(self ,value):
        self.g_max = value/10
    
    def set_b_min_value(self ,value):
        self.b_min = value
    
    def set_b_max_value(self ,value):
        self.b_max = value/10
        
    def set_brightness(self, value):
        self.brightness = value
        self.r_min = self.brightness
        self.g_min = self.brightness
        self.b_min = self.brightness
        self.set_rgb_value()
        
    def set_contrast(self, value):
        self.contrast_coe = value/10
        self.r_max = self.contrast_coe
        self.g_max = self.contrast_coe
        self.b_max = self.contrast_coe
        self.set_rgb_value()
        
    def get_folder_from_file(self, filename):
        folder = filename
        while folder[-1] != '/':
            folder = folder[:-1]
        return folder
        
    
    def saveFileDialog(self):
        #self.openfile = False
        save_file_name = QFileDialog.getSaveFileName(self,'save as',\
                                                     self.saveFileDialog_folder,\
                                                     "Image files(*.jpg *.png)")
        if  save_file_name[0]:
            self.refresh_show()
            self.refresh_raw()
            cv2.imwrite(save_file_name[0], self.img_raw)
            self.saveFileDialog_folder = self.get_folder_from_file(save_file_name[0])

    
    def showFileDialog(self):
        self.fname = QFileDialog.getOpenFileName(self, 'Open file',\
                                                 self.showFileDialog_folder,\
                                                 "Image files(*.jpg *.png)")
        #加上判断文件类型的操作，试试try except
        if self.fname[0]:
            self.showFileDialog_folder = self.get_folder_from_file(self.fname[0])
            self.button_release.setChecked(False)
            self.button_live.setChecked(False)
            self.live_timer.stop()
            self.openfile = True
            self.rgb_initialize()
            self.img_raw = cv2.imread(self.fname[0])
            self.img_raw_not_cropped = self.img_raw            
            self.openfile_timer.start(40)
                      
    def rgb_initialize(self):
        self.r_min, self.r_max=0, 1
        self.g_min, self.g_max=0, 1
        self.b_min, self.b_max=0, 1
        self.brightness, self.contrast_coe = 0, 1
        self.set_rgb_value()
        
    def set_rgb_value(self):
        self.sld.r_min_sld.setValue(self.r_min)
        self.sld.r_max_sld.setValue(self.r_max*10)
        self.sld.g_min_sld.setValue(self.g_min)
        self.sld.g_max_sld.setValue(self.g_max*10)
        self.sld.b_min_sld.setValue(self.b_min)
        self.sld.b_max_sld.setValue(self.b_max*10)
        self.sld.bright_sld.setValue(self.brightness)
        self.sld.contrast_sld.setValue(self.contrast_coe*10)

    def sld_connect(self):
        self.sld.r_min_sld.valueChanged[int].connect(self.set_r_min_value)
        self.sld.r_max_sld.valueChanged[int].connect(self.set_r_max_value)
        self.sld.g_min_sld.valueChanged[int].connect(self.set_g_min_value)
        self.sld.g_max_sld.valueChanged[int].connect(self.set_g_max_value)
        self.sld.b_min_sld.valueChanged[int].connect(self.set_b_min_value)
        self.sld.b_max_sld.valueChanged[int].connect(self.set_b_max_value)
        self.sld.bright_sld.valueChanged[int].connect(self.set_brightness)
        self.sld.contrast_sld.valueChanged[int].connect(self.set_contrast)

    def change_contrast(self, img):
        img_contra = img#.copy()
        if len(img.shape) == 3:
            #r,g,b = cv2.split(img)
            #r_scale = (self.r_max-self.r_min)/255
            #g_scale = (self.g_max-self.g_min)/255
            #b_scale = (self.b_max-self.b_min)/255
            scale = np.zeros(3)
            scale[0] = self.r_max
            scale[1] = self.g_max
            scale[2] = self.b_max
            bias = np.zeros(3)
            bias[0] = self.r_min
            bias[1] = self.g_min
            bias[2] = self.b_min
            '''
            scale[0] = (self.r_max-self.r_min)/255
            scale[1] = (self.g_max-self.g_min)/255
            scale[2] = (self.b_max-self.b_min)/255
            minim = np.zeros(3)
            minim[0] = self.r_min
            minim[1] = self.g_min
            minim[2] = self.b_min
            maxim = np.zeros(3)
            maxim[0] = self.r_max
            maxim[1] = self.g_max
            maxim[2] = self.b_max
            '''
            for k in range(3):
                img_contra[:,:,k] = go_fast(img_contra[:,:,k],bias[k],scale[k])
            #img_contra[:,:,0] = np.uint8(r*r_scale+self.r_min)
            #img_contra[:,:,1] = np.uint8(g*g_scale+self.g_min)
            #img_contra[:,:,2] = np.uint8(b*b_scale+self.b_min)
        else:
            #self.gray_min = 0.299*self.r_min + 0.587*self.g_min + 0.114*self.b_min
            #self.gray_max = 0.299*self.r_max + 0.587*self.g_max + 0.114*self.b_max
            #gray_scale = np.array((self.gray_max-self.gray_min)/255).astype('float16')
            #img_contra = np.uint8(img*gray_scale+self.gray_min)
            img_contra = go_fast(img_contra, self.brightness, self.contrast_coe)
        return img_contra
          
    
    def update_release(self):
        #self.button_live.setChecked(False)
        #self.button_release.setChecked(True)
        self.live_timer.stop()
        self.openfile_timer.stop()        
        #self.openfile = False
        #self.img_raw = self.camera.last_frame
        img_release_temp = []
        for i in range(5):
            self.refresh_show()
            self.show_on_screen()
            self.refresh_raw()
            while os.path.isfile(self.save_folder+'/'+self.date+'-'+str(self.release_count)+'.jpg'):
                self.release_count += 1
            img_release_temp.append(self.img_raw)
        img_release = img_release_temp[0].astype(int)
        for img in img_release_temp[1:]:
            img_release += img.astype(int)
        #print(len(img_release_temp))
        img_release = img_release / len(img_release_temp)
        img_release = img_release.astype(np.uint8)
        cv2.imwrite(self.save_folder+'/'+self.date+'-'+str(self.release_count)+'.jpg', img_release)
        cv2.imshow('released', img_release)
        self.live_timer.start(40)        
        
              
    def start_live(self):
        #self.button_release.setChecked(False)
        self.button_live.setChecked(True)
        self.openfile_timer.stop()
        self.openfile = False
        self.movie_thread = MovieThread(self.camera)      
        self.movie_thread.start()
        self.live_timer.start(40)
               
    def update_live(self):
        #self.img_raw = self.camera.last_frame
        self.refresh_show()
        self.show_on_screen()
    
    def refresh_show(self):  
        #self.img_show = cv2.pyrDown(self.img_raw)
        if self.openfile:
            self.img_raw = self.img_raw_not_cropped
        else:
            self.img_raw = self.camera.last_frame
        self.img_show = self.img_raw#其实这两行代码结果是差不多的
        self.display_resize()#先resize是为了加快运算
        if self.CP:
            self.left_crop = int(self.img_show.shape[1]*0.17)
            self.right_crop = int(self.img_show.shape[1]*0.83)
            self.img_show = self.img_show[:, self.left_crop:self.right_crop]
            #self.display_resize()
            self.img_show = np.require(self.img_show, np.uint8, 'C')
            self.display_resize()
            self.left_crop_raw = int(self.img_raw.shape[1]*0.17)
            self.right_crop_raw = int(self.img_raw.shape[1]*0.83)  
            self.img_raw = self.img_raw[:, self.left_crop_raw:self.right_crop_raw]

        
        if self.zoom_draw_start :
            cv2.rectangle(self.img_show,(self.mouse_rec_x1,self.mouse_rec_y1),\
                          (self.mouse_rec_x2, self.mouse_rec_y2),(0,0,255),2)
        elif self.zoomed:
            #self.mouse_pos_ratio_change_rec()
            scale_ratio = self.img_raw.shape[1]/self.img_bfzoom_width
            self.img_show = self.img_raw[int(self.mouse_rec_y1*scale_ratio):int(self.mouse_rec_y2*scale_ratio),\
                                         int(self.mouse_rec_x1*scale_ratio):int(self.mouse_rec_x2*scale_ratio)]
            #print(self.img_show.shape[0],self.img_show.shape[1])
            self.img_show = np.require(self.img_show, np.uint8, 'C')
            self.display_resize()
            #self.img_show = cv2.blur(self.img_show, (10,10))
            
        if self.SB:
            background_cut = self.background
            if self.zoomed:
                #print(self.img_bfzoom_width,self.img_bfzoom_height)
                background_cut = cv2.resize(self.background,(self.img_raw.shape[1], \
                                                         self.img_raw.shape[0]))
                background_cut = background_cut[int(self.mouse_rec_y1*scale_ratio):int(self.mouse_rec_y2*scale_ratio),\
                                         int(self.mouse_rec_x1*scale_ratio):int(self.mouse_rec_x2*scale_ratio)]

            background_cut = cv2.resize(background_cut,(self.img_show.shape[1], \
                                                         self.img_show.shape[0]))            
            
            self.img_show = background_divide(self.img_show, background_cut, self.background_norm)           
               
        if self.gray:
            self.img_show = cv2.cvtColor(self.img_show,cv2.COLOR_BGR2GRAY)
            self.img_show = self.change_contrast(self.img_show)
        else:
            self.img_show = cv2.cvtColor(self.img_show,cv2.COLOR_BGR2RGB)
            self.img_show = self.change_contrast(self.img_show)
        

        if self.DT_draw:
            self.mouse_pos_ratio_change_line()
            cv2.line(self.img_show,(self.mouse_line_x1,self.mouse_line_y1),\
                    (self.mouse_line_x2, self.mouse_line_y2),(255,0,0),2)
            self.distance = np.sqrt((self.mouse_line_x2-self.mouse_line_x1)**2\
                                    +(self.mouse_line_y2-self.mouse_line_y1)**2)
            self.distance /= self.img_show.shape[0]
            if self.zoomed:
                zoom_ratio = (self.mouse_rec_y2 - self.mouse_rec_y1)/self.img_atmouse_height           
                self.distance *= zoom_ratio
            self.distance = self.distance*1000/self.magnification*self.calibrition
            self.distance_lbl.setText(str(round(self.distance,2))+' um')
        if self.CT_draw:
            if len(self.contrast_line) == 2:
                
                self.contrast \
                = calculate_contrast(self.img_show,\
                   self.contrast_line[0][0][0], self.contrast_line[0][0][1],\
                   self.contrast_line[0][1][0], self.contrast_line[0][1][1],\
                   self.contrast_line[1][0][0], self.contrast_line[1][0][1],\
                   self.contrast_line[1][1][0], self.contrast_line[1][1][1])
                #for i in range(len(xtemp)):
                 #   cv2.circle(self.img_show,(xtemp[i],ytemp[i]),1,(0,0,255))
                
                #self.contrast = 0
            else:
                self.contrast = 0
            self.contrast_lbl.setText(str(round(self.contrast,4)))
            for i in range(len(self.contrast_line)):
                cv2.line(self.img_show, \
                         (self.contrast_line[i][0][0], self.contrast_line[i][0][1]),\
                         (self.contrast_line[i][1][0], self.contrast_line[i][1][1]),\
                         (255,0,0),2)
        if len(self.draw_shape_list) > 0:
            for shape in self.draw_shape_list:
                if shape.prop == 1:
                    cv2.line(self.img_show, *shape.pos, shape.color, shape.width)
                elif shape.prop == 2:
                    cv2.rectangle(self.img_show, *shape.pos, shape.color, shape.width)
                elif shape.prop == 3:
                    cv2.circle(self.img_show, *shape.pos, shape.radius, shape.color,shape.width)

    def mouse_pos_ratio_change_rec(self):
        if self.img_atmouse_width != self.resize_show_width:
            self.mouse_rec_x1 = int(self.mouse_rec_x1/self.img_atmouse_width*\
                                   self.resize_show_width)
            self.mouse_rec_x2 = int(self.mouse_rec_x2/self.img_atmouse_width*\
                                   self.resize_show_width)
            self.img_atmouse_width = self.resize_show_width
        if self.img_atmouse_height != self.resize_show_height:
            self.mouse_rec_y1 = int(self.mouse_rec_y1/self.img_atmouse_height*\
                                   self.resize_show_height)
            self.mouse_rec_y2 = int(self.mouse_rec_y2/self.img_atmouse_height*\
                                   self.resize_show_height)
            self.img_atmouse_height = self.resize_show_height
    
    def mouse_pos_ratio_change_line(self):
        if self.img_bfDT_width != self.resize_show_width:
            self.mouse_line_x1 = int(self.mouse_line_x1/self.img_bfDT_width*\
                                   self.resize_show_width)
            self.mouse_line_x2 = int(self.mouse_line_x2/self.img_bfDT_width*\
                                   self.resize_show_width)
            self.img_bfDT_width = self.resize_show_width
        if self.img_bfDT_height != self.resize_show_height:
            self.mouse_line_y1 = int(self.mouse_line_y1/self.img_bfDT_height*\
                                   self.resize_show_height)
            self.mouse_line_y2 = int(self.mouse_line_y2/self.img_bfDT_height*\
                                   self.resize_show_height)
            self.img_bfDT_height = self.resize_show_height
            


    def show_on_screen(self):
        self.img_qi = self.np2qimage(self.img_show)
        self.pixmap = QPixmap(self.img_qi)
        self.lbl_main.setPixmap(self.pixmap)
        self.draw_hist()
    
    def refresh_raw(self):
        if self.SB:
            background_cut = cv2.resize(self.background,(self.img_raw.shape[1], \
                                                         self.img_raw.shape[0]))
            
            self.img_raw = background_divide(self.img_raw, background_cut, self.background_norm)           
        if self.gray:
            self.img_raw = cv2.cvtColor(self.img_raw,cv2.COLOR_BGR2GRAY)
            self.img_raw = self.change_contrast(self.img_raw)
        else:
            self.img_raw = cv2.cvtColor(self.img_raw,cv2.COLOR_BGR2RGB)
            self.img_raw = self.change_contrast(self.img_raw)
            self.img_raw = cv2.cvtColor(self.img_raw,cv2.COLOR_RGB2BGR)
        
   
    def draw_hist(self):
        counts = [256]
        interval = [0, 256]
        if len(self.img_show.shape) == 3:
            hist_r = cv2.calcHist([self.img_show], [0], None, counts,interval)
            hist_g = cv2.calcHist([self.img_show], [1], None, counts,interval)
            hist_b = cv2.calcHist([self.img_show], [2], None, counts,interval)
            
            hist_r = hist_r.reshape(len(hist_r))
            hist_g = hist_g.reshape(len(hist_g))
            hist_b = hist_b.reshape(len(hist_b))
            
            hist_r = hist_r/(max(hist_r)+1)*1000
            hist_g = hist_g/(max(hist_g)+1)*1000
            hist_b = hist_b/(max(hist_b)+1)*1000
            
            self.pw_hist.clear()
            self.pw_hist.plot(hist_r, pen = pg.mkPen(color = 'r', width = 2))
            self.pw_hist.plot(hist_g, pen = pg.mkPen(color = 'g', width = 2))
            self.pw_hist.plot(hist_b, pen = pg.mkPen(color = 'b', width = 2))
        else:
            hist_gray = cv2.calcHist([self.img_show], [0], None, counts,interval)
            hist_gray = hist_gray.reshape(len(hist_gray))
            hist_gray = hist_gray/(max(hist_gray)+1)*1000
            self.pw_hist.clear()
            self.pw_hist.plot(hist_gray)
    
               
    def display_resize(self):
        self.window_width = self.geometry().width()
        self.window_height = self.geometry().height()
        
        self.img_show_width = max(1, self.img_show.shape[1])
        self.img_show_height = max(1, self.img_show.shape[0])       
        self.scale_rate = min((self.window_width-270)/self.img_show_width, \
                              (self.window_height-125)/self.img_show_height)        
        self.resize_show_width = int(self.img_show_width*self.scale_rate)
        self.resize_show_height = int(self.img_show_height*self.scale_rate)
        #print(self.resize_width,self.resize_height)
        #self.lbl_main.resize(self.resize_width, self.resize_height)
        
        self.lbl_main.setFixedWidth(self.window_width-300)
        self.lbl_main.setFixedHeight(self.window_height-125)
        
        self.img_show = cv2.resize(self.img_show, (self.resize_show_width, self.resize_show_height))
    
    def np2qimage(self, img):
        if len(img.shape)==3:
            qimage = QImage(img[:], img.shape[1], img.shape[0],\
                          img.shape[1] * 3, QImage.Format_RGB888)
        else:
            qimage = QImage(img[:], img.shape[1], img.shape[0],\
                          img.shape[1] * 1, QImage.Format_Indexed8)
        return qimage
        

class MovieThread(QThread):
    def __init__(self,camera):
        super().__init__()
        self.camera = camera
        
    def run(self):
        self.camera.acquire_movie()
       
def restart():
    python = sys.executable
    os.execl(python, python, * sys.argv)



if __name__ == '__main__':
    
    '''
    date = time.strftime("%Y/%m/%d")
    filepath = 'F:/'+date
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    '''
    
    app = QApplication(sys.argv)
    
    splash = QSplashScreen(QPixmap('F:/Desktop2019.8.15/SonyView/support_file/Sony.png'))
    splash.show()
    splash.showMessage('Loading……')
    
    camera = Camera(0)
    camera.initialize()
    
    
    slid = MainWindow(camera)
    splash.close()
    sys.exit(app.exec_())
    
    camera.close_camera()
    
    