# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 16:31:08 2020

@author: HP
"""

import numpy as np
from PyQt5.QtWidgets import QWidget, QSlider, QVBoxLayout, QHBoxLayout, \
    QLabel, QApplication, QGridLayout, QPushButton, QCheckBox, QAction, \
    QFileDialog, QMainWindow, QDesktopWidget, QToolButton, QComboBox,\
    QMessageBox, QProgressBar, QSplashScreen, QLineEdit, QShortcut, QMenu,\
    QColorDialog
from PyQt5.QtCore import Qt, QThread, QTimer, QObject, pyqtSignal, QBasicTimer, \
    QEvent
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtMultimedia import QSound
import pyqtgraph as pg
import sys
import cv2
import os
import time
import json
from Camera import Camera
from BresenhamAlgorithm import Pos_of_Line, Pos_of_Circle, Pos_in_Circle, \
    Pos_of_Rec 
import copy
from numba import jit
from drawing import Line, Rectangle, Circle, Eraser, Point, Clear_All
import win32gui
import win32api
import win32con
sys.coinit_flags = 2
import warnings
warnings.simplefilter("ignore", UserWarning)
from pywinauto.controls.win32_controls import EditWrapper, ListBoxWrapper
import scipy.signal as signal
from Threads import StageThread, AutoFocusThread, FindFocusPlane, Scan,\
    LayerSearchThread, LargeScanThread
from auxiliary_func import go_fast, background_divide, get_folder_from_file,\
    matrix_divide, float2uint8, calculate_contrast, record_draw_shape,\
    calculate_angle
from auxiliary_class import RGB_Slider, ProgressBar, CameraNumEdit, \
    CalibrationEdit, ThicknessChoose, SearchingProperty, DropLabel, \
    CustomContrast, DeleteCustomContrast

          
class QComboBox(QComboBox):
    def wheelEvent(self, QWheelEvent):
        pass

class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.openfile = False
        self.initUI()

    
    def initUI(self):
        #self.file_dir_test()
        self.current_dir = os.path.abspath(__file__).replace('\\','/')
        self.current_dir = get_folder_from_file(self.current_dir)
        self.current_dir = self.current_dir + 'support_file/'
        self.current_bk_dir = self.current_dir + 'background/'
        self.gray = False
        self.img_raw = cv2.imread(self.current_dir+'no_camera.png')
        self.img_show = cv2.imread(self.current_dir+'no_camera.png')
        self.img_release = cv2.imread(self.current_dir+'no_camera.png')
        self.canvas = np.zeros(self.img_show.shape, dtype = np.uint8)
        self.canvas_blank = np.zeros((self.img_show.shape[0], self.img_show.shape[1]), dtype = int)
        self.custom_contrast_file = self.current_dir + 'custom_contrast.txt'
        
        if self.img_show is None:
            self.img_show = np.zeros((512,512,3), np.uint8)
            self.img_raw = np.zeros((512,512,3), np.uint8)
            QMessageBox.critical(self, "Missing file", 'The no_camera.png file '
                                 'is not found. Please check support_file')
        self.bk_filename = self.current_bk_dir+'x5.png'
        self.background_norm = np.zeros(3)
        self.bk_error = False
        self.get_bk_normalization()
        try:
            with open(self.current_dir+'saveto.txt') as f:
                self.release_folder = f.read()
        except:
            self.release_folder = 'C:/'
            QMessageBox.critical(self, "Missing file", 'The supporting saveto.txt '
                                  'file is missing.')
        self.date = time.strftime("%m-%d-%Y")
        self.release_count = 1
        
        self.selectbk_folder = 'C:/'
        self.showFileDialog_folder = 'C:/'
        self.saveFileDialog_folder = 'C:/'
        
        try:
            with open(self.current_dir+'calibration.txt') as f:
                self.calibration = float(f.read())
        except:
            self.calibration = 14.33
            QMessageBox.critical(self, "Missing file", 'The supporting calibration.txt '
                                  'file is missing. Calibration is set to default as'
                                  '14.33')
        try:
            with open(self.current_dir+'camera.txt') as f:
                self.camera_num = int(f.read())
        except:
            self.camera_num = 0
            QMessageBox.critical(self, "Missing file", 'The supporting camera.txt '
                                  'file is missing.')
        self.camera = Camera(self.camera_num)
        self.camera.initialize()
        
        
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        
        self.mouse_pos_initial()
        
        self.obtained_plane_para = [0,0,-1,0]#平面
        self.substrate_thickness = '285nm'
         
        openBK = QAction('Select BK', self)
        openBK.triggered.connect(self.select_background)
        
        openFile = QAction('Open file', self)
        openFile.triggered.connect(self.showFileDialog)
        openFile.setIcon(QIcon(self.current_dir+'openfile.png'))
        openFile.setShortcut('Ctrl+O')
        
        saveFile = QAction('Save as', self)
        saveFile.triggered.connect(self.saveFileDialog)
        saveFile.setIcon(QIcon(self.current_dir+'save.png'))
        saveFile.setShortcut('Ctrl+S')
        
        show_scale = QAction('Show scale', self, checkable = True)
        show_scale.setChecked(True)
        show_scale.triggered.connect(self.show_scale_method)
        self.show_scale = True
        
        self.developer_options = QAction('Developer options', self, checkable = True)
        self.developer_options.triggered.connect(self.show_developer_options)
        
        capture_BK = QAction('Capture BK', self)
        capture_BK.triggered.connect(self.capture_background)
        
        stage = QAction('Stage', self)
        stage.triggered.connect(self.stage)
        
        autofocus = QAction('Auto focus', self)
        autofocus.triggered.connect(self.autofocus)
        
        find_focus_plane = QAction('Find Focus Plane', self)
        find_focus_plane.triggered.connect(self.find_focus_plane)
        
        scan = QAction('Scan', self)
        scan.triggered.connect(self.scan)
        
        layer_search = QAction('Layer search', self)
        layer_search.triggered.connect(self.layer_search)
        
        large_scan = QAction('Large Scan', self)
        large_scan.triggered.connect(self.large_scan)
        
        theme = QAction('Theme', self)
        theme.triggered.connect(self.change_theme)
        
        restart = QAction('Restart', self)
        restart.triggered.connect(self.restart_program)
        
        set_calibration = QAction('Calibration', self)
        set_calibration.triggered.connect(self.set_calibration)
        
        set_cam_num = QAction('Camera number', self)
        set_cam_num.triggered.connect(self.set_camera_number)
        
        help_contact = QAction('Contact', self)
        help_contact.triggered.connect(self.contact)
        
        help_about = QAction('About', self)
        help_about.triggered.connect(self.about)
        
        #acknowledge = QAction('Acknowledgement', self)
        #acknowledge.triggered.connect(self.acknowledgement)
        
        self.menubar = self.menuBar()
        fileMenu = self.menubar.addMenu('&File')
        fileMenu.addAction(openFile)
        fileMenu.addAction(saveFile)
        fileMenu.addAction(openBK)
        
        toolMenu = self.menubar.addMenu('&Tools')
        toolMenu.addAction(show_scale)
        toolMenu.addAction(capture_BK)
        toolMenu.addAction(self.developer_options)
        toolMenu.addAction(restart)
        
        settingMenu = self.menubar.addMenu('&Setting')
        settingMenu.addAction(set_calibration)
        settingMenu.addAction(set_cam_num)
        settingMenu.addAction(theme)
        
        HelpMenu = self.menubar.addMenu('Help')
        HelpMenu.addAction(help_contact)
        HelpMenu.addAction(help_about)
        #HelpMenu.addAction(acknowledge)
        
        self.developerMenu = self.menubar.addMenu('Developer options')
        self.developerMenu.addAction(autofocus)
#        toolMenu.addAction(stage)
        self.developerMenu.addAction(find_focus_plane)
        self.developerMenu.addAction(scan)
        self.developerMenu.addAction(layer_search)
        self.developerMenu.addAction(large_scan)
        self.developerMenu.menuAction().setVisible(False)

        initial_size = QAction('Home',self)
        initial_size.triggered.connect(self.initial_size)
        
        self.open_file_button = QToolButton()
        self.open_file_button.setIcon(QIcon(self.current_dir + 'openfile.png'))
        self.open_file_button.setToolTip('Open file (Ctrl+O)')
#        self.open_file_button.setShortcut('Ctrl+O')
        self.open_file_button.clicked.connect(self.showFileDialog)
        
        self.save_file_button = QToolButton()
        self.save_file_button.setIcon(QIcon(self.current_dir + 'save.png'))
        self.save_file_button.setToolTip('Save file (Ctrl+S)')
#        self.save_file_button.setShortcut('Ctrl+S')
        self.save_file_button.clicked.connect(self.saveFileDialog)
        
        self.zoom_in_button = QToolButton()
        self.zoom_in_button.setIcon(QIcon(self.current_dir+'zoom_in.png'))
        self.zoom_in_button.setToolTip('Zoom in')
        self.zoom_in_button.clicked.connect(self.zoom_in)
        self.zoom_in_button.setCheckable(True)
        #self.zoom_in_button.setChecked(False)
        #self.zoom_in_button.setText("zoom in")
        self.zoom_draw = False
        self.zoom_draw_start = False
        self.zoomed = False
        
        self.draw_shape_action_list = []
        self.draw_shape_list = []
        self.draw_shape_action_list_for_redo = []
        self.draw_shape_count = 1
        
        self.straight_line_button = QToolButton()
        self.straight_line_button.setIcon(QIcon(self.current_dir+'straight_line.png'))
        self.straight_line_button.setToolTip('Draw straight line')
        self.straight_line_button.clicked.connect(self.draw_straight_line)
        self.straight_line_button.setCheckable(True)
        self.draw_shape_line = False
        self.drawing_shape_line = False
        self.draw_shape = False
        
        straight_line_tool_menu = QMenu()
        show_distance_checkmenu = QAction('Show Distance', self, checkable = True)
        show_distance_checkmenu.triggered.connect(self.show_distance_method)
        show_distance_checkmenu.setChecked(False)
        straight_line_tool_menu.addAction(show_distance_checkmenu)
        self.show_distance = False
        self.straight_line_button.setMenu(straight_line_tool_menu) 
        self.straight_line_button.setPopupMode(QToolButton.MenuButtonPopup)
        
        self.rectangle_button = QToolButton()
        self.rectangle_button.setIcon(QIcon(self.current_dir+'square.png'))
        self.rectangle_button.setToolTip('Draw rectangle')
        self.rectangle_button.clicked.connect(self.draw_rectangle)
        self.rectangle_button.setCheckable(True)
        self.draw_shape_rectangle = False
        self.drawing_shape_rectangle = False
        
        rectangle_tool_menu = QMenu()
        show_side_length_checkmenu = QAction('Show Side Length', self, checkable = True)
        show_side_length_checkmenu.triggered.connect(self.show_side_length_method)
        show_side_length_checkmenu.setChecked(False)
        rectangle_tool_menu.addAction(show_side_length_checkmenu)
        self.show_side_length = False
        self.rectangle_button.setMenu(rectangle_tool_menu) 
        self.rectangle_button.setPopupMode(QToolButton.MenuButtonPopup)
        
        self.circle_button = QToolButton()
        self.circle_button.setIcon(QIcon(self.current_dir+'circle.png'))
        self.circle_button.setToolTip('Draw circle')
        self.circle_button.clicked.connect(self.draw_circle)
        self.circle_button.setCheckable(True)
        self.draw_shape_circle = False
        self.drawing_shape_circle = False
        
        circle_tool_menu = QMenu()
        show_radius_checkmenu = QAction('Show Radius', self, checkable = True)
        show_radius_checkmenu.triggered.connect(self.show_radius_method)
        show_radius_checkmenu.setChecked(False)
        circle_tool_menu.addAction(show_radius_checkmenu)
        self.show_radius = False
        self.circle_button.setMenu(circle_tool_menu) 
        self.circle_button.setPopupMode(QToolButton.MenuButtonPopup)
        
        self.eraser_button = QToolButton()
        self.eraser_button.setIcon(QIcon(self.current_dir+'eraser.png'))
        self.eraser_button.setToolTip('Eraser')
        self.eraser_button.clicked.connect(self.erase_shape)
        self.eraser_button.setCheckable(True)
        self.erase = False
        self.drawing_eraser = False
        
        self.undo_draw_button = QToolButton()
        self.undo_draw_button.setIcon(QIcon(self.current_dir+'undo_gray_opacity.png'))
        self.undo_draw_button.setToolTip('Undo  Ctrl+Z')
        self.undo_draw_button.clicked.connect(self.undo_draw)
        self.undo_draw_button.setShortcut('Ctrl+Z')
        
        self.redo_draw_button = QToolButton()
        self.redo_draw_button.setIcon(QIcon(self.current_dir+'redo_gray_opacity.png'))
        self.redo_draw_button.setToolTip('Redo  Ctrl+Y')
        self.redo_draw_button.clicked.connect(self.redo_draw)
        self.redo_draw_button.setShortcut('Ctrl+Y')
        
        self.clear_draw_button = QToolButton()
        self.clear_draw_button.setIcon(QIcon(self.current_dir+'clear.png'))
        self.clear_draw_button.setToolTip('Clear drawing')
        self.clear_draw_button.clicked.connect(self.clear_draw)
        
        self.angle_button = QToolButton()
        self.angle_button.setIcon(QIcon(self.current_dir+'angle_measurement.png'))
        self.angle_button.setToolTip('Measure angle')
        self.angle_button.clicked.connect(self.angle_measurement)
        self.angle_button.setCheckable(True)
        self.start_angle_measurement = False
        self.base_line = []
        
        self.target_button = QToolButton()
        self.target_button.setIcon(QIcon(self.current_dir+'target.png'))
        self.target_button.setToolTip('Layer searching')
        self.target_button.clicked.connect(self.large_scan)
        
        angle_tool_menu = QMenu()
        choose_baseline = QAction('Choose Base Line', self)
        choose_baseline.triggered.connect(self.choose_base_line)
        clear_baseline = QAction('Clear Base Line', self)
        clear_baseline.triggered.connect(self.clear_base_line)
        angle_tool_menu.addAction(choose_baseline)
        #angle_tool_menu.addAction(clear_baseline)
        self.choosing_base_line = False
        self.angle_button.setMenu(angle_tool_menu) 
        self.angle_button.setPopupMode(QToolButton.MenuButtonPopup)
        
        self.graphene_button = QToolButton()
        self.graphene_button.setIcon(QIcon(self.current_dir+'graphene.png'))
        self.graphene_button.setToolTip('graphene auto detection')
        self.graphene_button.clicked.connect(self.graphene_hunt)
        
        self.toolbar_file = self.addToolBar('file')
        self.toolbar_file.addWidget(self.open_file_button)
        self.toolbar_file.addWidget(self.save_file_button)
        
        self.toolbar_zoom = self.addToolBar('zoom')
        #self.toolbar1.addAction(initial_size)
        self.toolbar_zoom.addWidget(self.zoom_in_button)
        
        self.toolbar_drawing = self.addToolBar('drawing')
        self.toolbar_drawing.addWidget(self.straight_line_button)
        self.toolbar_drawing.addWidget(self.rectangle_button)
        self.toolbar_drawing.addWidget(self.circle_button)
        self.toolbar_drawing.addWidget(self.eraser_button)
        self.toolbar_drawing.addWidget(self.undo_draw_button)
        self.toolbar_drawing.addWidget(self.redo_draw_button)
        self.toolbar_drawing.addWidget(self.clear_draw_button)
        
        self.toolbar_advanced_tools = self.addToolBar('advanced tools')
        self.toolbar_advanced_tools.addWidget(self.angle_button)
        
        self.toolbar_search = self.addToolBar('layer search')
        self.toolbar_search.addWidget(self.target_button)
        
        self.toolbar = self.addToolBar(' ')

        self.sld = RGB_Slider()
        self.rgb_initialize()
        self.sld_connect()
                        
        self.button_release = QPushButton('Release', self)
        self.button_release.clicked.connect(self.update_release)
        self.button_release.setToolTip('Ctrl+R')
        self.button_release.setShortcut('Ctrl+R')
        #self.button_release.setCheckable(True)
        
        self.button_live = QPushButton('Live View', self)
        self.button_live.clicked.connect(self.start_live)
        self.button_live.setCheckable(True)
        
        self.button_save_as = QPushButton('Save as', self)
        self.button_save_as.clicked.connect(self.saveFileDialog)
        
        button_reset_contrast = QPushButton('Reset Contrast', self)
        button_reset_contrast.clicked.connect(self.rgb_initialize)
        
        self.combo_custom_contrast = QComboBox(self)
        self.read_previous_custom_contrast()
        try:
            self.generate_custom_contrast_items()
        except:
            QMessageBox.critical(self, "File damaged", "The supporting file custom_contrast.txt "
                                  "has been damaged! All custom settings will be deleted.")
            os.remove(self.custom_contrast_file)
            self.read_previous_custom_contrast()
            self.generate_custom_contrast_items()
        self.combo_custom_contrast.activated[str].connect(self.custom_contrast)
        self.combo_custom_contrast.setFixedHeight(26)
        
        self.hbox_change_contrast = QHBoxLayout()
        self.hbox_change_contrast.addWidget(button_reset_contrast)
        self.hbox_change_contrast.addWidget(self.combo_custom_contrast)
        
        self.button_saveto = QPushButton('Save path', self)
        self.button_saveto.setToolTip('This is the folder where your released files will be saved')
        self.button_saveto.clicked.connect(self.save_path_setting)
        
        self.release_folder_lbl = QLabel(self)
        if len(self.release_folder) > 20:
            self.release_folder_lbl.setText('...'+self.release_folder[-25:])
        else:
            self.release_folder_lbl.setText(self.release_folder)
        
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

        self.crop_left_rate = 0.17
        self.crop_right_rate = 0.83
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
        
        self.lbl_main = DropLabel('',self)
        self.lbl_main.new_img.connect(self.accept_new_img)
        self.lbl_main.setAlignment(Qt.AlignCenter)
        self.lbl_main.setPixmap(self.pixmap)
        
        
        self.pw_hist = pg.PlotWidget()
        self.pw_hist.setFixedHeight(300)
        #self.lbl.resize(1920*0.8,1080*0.8)
        
        self.hbox_button = QHBoxLayout()
        self.hbox_button.addWidget(self.button_save_as)
        self.hbox_button.addWidget(self.button_release)
        self.hbox_button.addWidget(self.button_live)
        self.hbox_button.addWidget(cb_gray)
        self.hbox_button.addWidget(cb_sb)
        self.hbox_button.addWidget(self.cb_crop)
        
        #self.hbox_button_layout = QHBoxLayout()
        #self.hbox_button_layout.addLayout(self.hbox_button)
        
        self.vbox_l = QVBoxLayout()
        self.vbox_l.addWidget(self.lbl_main)
        self.vbox_l.addLayout(self.hbox_button)
        
        self.hbox_distance = QHBoxLayout()
        self.hbox_distance.addWidget(self.cb_tool_distance)
        self.hbox_distance.addWidget(self.distance_lbl)
        
        self.hbox_contrast = QHBoxLayout()
        self.hbox_contrast.addWidget(self.cb_tool_contrast)
        self.hbox_contrast.addWidget(self.contrast_lbl)
        
        self.vbox_r = QVBoxLayout()
        self.vbox_r.addWidget(self.combo_mag, Qt.AlignCenter)
        self.vbox_r.addStretch(1)
        self.vbox_r.addLayout(self.hbox_distance)
        self.vbox_r.addStretch(0.5)
        self.vbox_r.addLayout(self.hbox_contrast)
        self.vbox_r.addStretch(1)
        self.vbox_r.addWidget(self.pw_hist)
        self.vbox_r.addStretch(1)
        self.vbox_r.addLayout(self.sld.grid)
        #vbox_r.addStretch(1)
        self.vbox_r.addLayout(self.hbox_change_contrast)
        self.vbox_r.addStretch(2)
        self.vbox_r.addWidget(self.button_saveto, Qt.AlignBottom)
        #vbox_r.addStretch(1)
        self.vbox_r.addWidget(self.release_folder_lbl)
        self.vbox_r.addStretch(1)
        
        
        self.hbox = QHBoxLayout()
        self.hbox.addLayout(self.vbox_l)
        self.hbox.addLayout(self.vbox_r)
        
        self.central_widget = QWidget()
       
        self.layout = QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)
        self.layout.addLayout(self.hbox)
        
        self.movie_thread = MovieThread(self.camera)
        
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

        self.initial_window_width = round(self.screen_width*0.5)
        self.initial_window_height = round(self.screen_height*0.7)
        self.window_normal = False
        self.resize(self.initial_window_width, self.initial_window_height)
        self.setWindowTitle('Sony Remote (v2.0)')
        self.setWindowIcon(QIcon(self.current_dir+'shutter.jpg'))
        self.setObjectName('MainWindow')
        
#        self.setStyleSheet('#MainWindow{background-color: green}')
    
    
    
    def large_scan(self):
        self.large_scan_thread = LargeScanThread(self.camera, self.substrate_thickness)
        self.search_property_widget = SearchingProperty()
        self.search_property_widget.show()
        self.search_property_widget.confirmed.connect(self.get_search_property)
        
    def get_search_property(self, s):
        if s == 'confirmed':
            self.large_scan_thread.thickness = self.search_property_widget.thickness
            self.large_scan_thread.magnification = self.search_property_widget.magnification
            self.large_scan_thread.material = self.search_property_widget.material
            self.search_property_widget.close()
            self.large_scan_thread.start()
    
    def layer_search(self):
        self.layer_search_thread = LayerSearchThread(self.substrate_thickness)
        self.choosethickness_widget = ThicknessChoose()
        self.choosethickness_widget.show()
        self.choosethickness_widget.confirmed.connect(self.choose_thickness_search)
        #self.layer_search_thread.start()
        
    def choose_thickness_search(self, s):
        if s == 'confirmed':
            self.layer_search_thread.material = self.choosethickness_widget.material
            self.layer_search_thread.thickness = self.choosethickness_widget.thickness
            self.choosethickness_widget.close()
            self.layer_search_thread.start()
        
        
    def scan(self):
        self.scan_thread = Scan(self.camera, self.obtained_plane_para)
        self.scan_thread.scan_stop.connect(self.recv_scan_stop)
        self.scan_thread.start()
        self.layer_search()
        
        
    def recv_scan_stop(self,s):
        if s == 'stop':
            pass
#            self.layer_search_thread.terminate()
       
    def find_focus_plane(self):
        self.find_focus_plane_thread = FindFocusPlane(self.camera)
        self.find_focus_plane_thread.find_focus_plane_stop.connect(self.recv_find_focus_plane_stop)
        self.find_focus_plane_thread.start()
        
    def recv_find_focus_plane_stop(self, s):
        if s == 'stop':
            print('find focus plane finished')
            self.find_focus_plane_thread.terminate()
            self.obtained_plane_para = self.find_focus_plane_thread.para
            self.scan()
        
    def autofocus(self):
        self.autofocus_thread = AutoFocusThread(self.camera)
        self.autofocus_thread.focus_finish.connect(self.recv_focus_stop)
        self.autofocus_thread.start()
        
        
    def recv_focus_stop(self, s):
        print('123')
        if s == 'stop':
            self.autofocus_thread.terminate()
        
          
    def stage(self):
        self.stage_thread = StageThread(self.camera)
        self.stage_thread.stagestop.connect(self.recv_stage_stop)
        self.stage_thread.start()
        
    def recv_stage_stop(self, s):
#        print('123')
        if s == 'stop':
            self.stage_thread.terminate()
    
    
    def show_developer_options(self):
        if self.developer_options.isChecked():
            reply = QMessageBox.information(self, "Developer options", 'Do you want to '
                                          'open developer options? These tools are designed '
                                          'for advanced debugging usage.',
                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                self.developerMenu.menuAction().setVisible(True)
        else:
            self.developerMenu.menuAction().setVisible(False)
    
    
    def change_theme(self):
        col = QColorDialog.getColor()

        if col.isValid():
            self.setStyleSheet("#MainWindow { background-color: %s }"
                % col.name())
        pass
    
    
    def custom_contrast(self, text):
        if text == 'Custom':
            i = 1
            while i < 1000:
                if 'custom(' + str(i) + ')' in self.custom_contrast_dic:
                    i += 1
                else:
                    break
            self.custom_contrast_widget = CustomContrast('custom(' + str(i) + ')')
            self.custom_contrast_widget.confirmed.connect(self.new_custom_contrast)
            self.custom_contrast_widget.show()
        elif text == 'Delete':
            self.delete_custom_contrast_widget = DeleteCustomContrast(sorted(self.custom_contrast_list))
            self.delete_custom_contrast_widget.confirmed.connect(self.delete_custom_contrast)
            self.delete_custom_contrast_widget.show()
            pass
        else:
            self.brightness, self.contrast_coe, self.r_min, self.r_max, self.g_min, \
            self.g_max, self.b_min, self.b_max = self.custom_contrast_dic[text]
            self.set_rgb_value()
    
    
    def delete_custom_contrast(self, s):
        if s == 'confirmed':
            for item in self.delete_custom_contrast_widget.delte_list:
                self.custom_contrast_dic.pop(item)
            js = json.dumps(self.custom_contrast_dic)
            with open(self.custom_contrast_file, 'w') as f:
                f.write(js)
            self.delete_custom_contrast_widget.close()
            self.combo_custom_contrast.clear()
            self.generate_custom_contrast_items()

    
    def new_custom_contrast(self, s):
        if s == 'confirmed':
            record_contrast = [self.brightness, self.contrast_coe, self.r_min, \
                               self.r_max, self.g_min, self.g_max, self.b_min, self.b_max]
            self.custom_contrast_dic[self.custom_contrast_widget.name] = record_contrast
            self.custom_contrast_widget.close()
            js = json.dumps(self.custom_contrast_dic)
            with open(self.custom_contrast_file, 'w') as f:
                f.write(js)
            self.combo_custom_contrast.clear()
            self.generate_custom_contrast_items()
            
    def generate_custom_contrast_items(self):        
        self.custom_contrast_list = list(self.custom_contrast_dic.keys())[1:]
        self.combo_custom_contrast.addItem('Custom')
        if len(self.custom_contrast_list) > 0:
            self.combo_custom_contrast.addItems(sorted(self.custom_contrast_list))
        self.combo_custom_contrast.addItem('Delete')
    
    def read_previous_custom_contrast(self):
        if not os.path.isfile(self.custom_contrast_file):
            f = open(self.custom_contrast_file, 'w')
            f.close()
        with open(self.custom_contrast_file, 'r') as f:
            js = f.read()
        try:
            self.custom_contrast_dic = json.loads(js)
            print(self.custom_contrast_dic)
        except:
            QMessageBox.critical(self, "File damaged", "The supporting file custom_contrast.txt "
                                  "has been damaged! All custom settings will be deleted.")
            dic = {'Custom' : [0, 0, 0, 0, 0, 0, 0, 0]}
            js = json.dumps(dic)
            with open(self.custom_contrast_file, 'w') as f:
                f.write(js)
            self.custom_contrast_dic = dic
            
        
    def show_scale_method(self):
        if self.show_scale:
            self.show_scale = False
        else:
            self.show_scale = True
    
    def accept_new_img(self, s): 
        if s == 'new':
            self.showFileDialog_folder = get_folder_from_file(self.lbl_main.img_path)
            self.button_release.setChecked(False)
            self.button_live.setChecked(False)
            self.live_timer.stop()
            self.openfile = True
            self.rgb_initialize()
            self.img_raw = cv2.imread(self.lbl_main.img_path)
            self.img_raw_not_cropped = self.img_raw            
            self.openfile_timer.start(40)
#            print('yes')
    
    def set_calibration(self):
        self.input_calibration = CalibrationEdit(self.calibration)
        self.input_calibration.save_once_button.clicked.connect(self.recv_new_calibration)
        self.input_calibration.save_later_button.clicked.connect(self.recv_save_new_calibration)
        self.input_calibration.show()
        
    
    def recv_new_calibration(self):
        s = self.input_calibration.calibration
        try:
            float(s)
        except:
            self.calibration_warning()
        else:
            if str.isalpha(str(float)):
                self.calibration_warning()
            elif not 0.1 <= float(s) <= 30:
                self.calibration_warning()
            else:
                self.calibration = float(s)
                self.input_calibration.close()
            
            
    def recv_save_new_calibration(self):
        self.recv_new_calibration()
        reply = QMessageBox.warning(self, "Warning", 'Do you want to save this '+\
                                    'new calibration for later use?',+\
                                    QMessageBox.No | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            try:
                with open(self.current_dir+'calibration.txt','w') as f:
                    f.write(str(self.calibration))
            except:
                QMessageBox.critical(self, "Error writing file", "The supporting calibration.txt "
                                  "file can't be written!")
    
    
    def calibration_warning(self):
        self.input_calibration.close()
        self.input_calibration.con_but_click_num = 0
        reply = QMessageBox.warning(self, "Warning", 'Calibration can only be '+\
                                    'decimals > 0.1 and <30. Do you want to '+
                                    'try again? ', +\
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            self.input_calibration.show()
    
    
    def set_camera_number(self):
        self.input_cam_num = CameraNumEdit(self.camera_num)
        self.input_cam_num.save_once_button.clicked.connect(self.recv_camera_number)
        self.input_cam_num.save_later_button.clicked.connect(self.recv_save_camera_number)
        self.input_cam_num.show()
        
        
    def recv_camera_number(self):
        s = self.input_cam_num.camera_num
        try: 
            int(s)
        except:
            self.input_cam_num.close()
            self.input_cam_num.con_but_click_num = 0
            reply = QMessageBox.warning(self, "Warning", 'Camera number can only be '+\
                                        'Integer. Do you want to try again? ', +\
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                self.input_cam_num.show()
        else:
            self.camera.close_camera()
            self.live_timer.stop()
            self.movie_thread.terminate()
            self.camera_num = int(s)
            self.camera = Camera(self.camera_num)
            self.camera.initialize()
            self.movie_thread = MovieThread(self.camera)
            self.movie_thread.start()
            self.live_timer.start(40)
            self.input_cam_num.close()
    
    def recv_save_camera_number(self):
        self.recv_camera_number()
        reply = QMessageBox.warning(self, "Warning", 'Do you want to save this '+\
                                    'new camera number for later use?',+\
                                    QMessageBox.No | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            try:
                with open(self.current_dir+'camera.txt','w') as f:
                    f.write(str(self.camera_num))
            except:
                QMessageBox.critical(self, "Error writing file", "The supporting camera.txt "
                                  "file can't be written!")


          
    def undo_redo_setting(self):
        self.undo_draw_button.setIcon(QIcon(self.current_dir+'undo.png'))
        self.draw_shape_action_list_for_redo = []
        self.redo_draw_button.setIcon(QIcon(self.current_dir+'redo_gray_opacity.png'))    

    def undo_draw(self):
        if len(self.draw_shape_action_list) > 0:
            self.draw_shape_action_list_for_redo.append(self.draw_shape_action_list[-1])
            self.redo_draw_button.setIcon(QIcon(self.current_dir+'redo.png'))
            self.draw_shape_action_list.pop()
            if len(self.draw_shape_action_list) == 0:
                self.undo_draw_button.setIcon(QIcon(self.current_dir+'undo_gray_opacity.png'))

    def redo_draw(self):
        if len(self.draw_shape_action_list_for_redo) > 0:
            self.draw_shape_action_list.append(self.draw_shape_action_list_for_redo[-1])
            self.undo_draw_button.setIcon(QIcon(self.current_dir+'undo.png'))
            self.draw_shape_action_list_for_redo.pop()
            if len(self.draw_shape_action_list_for_redo) == 0:
                self.redo_draw_button.setIcon(QIcon(self.current_dir+'redo_gray_opacity.png'))
    
    def clear_draw(self):
#        reply = QMessageBox.warning(self, "warning", 'Do you want to clear all '+\
#                                        'the drawing?', +\
#                                    QMessageBox.No | QMessageBox.No, QMessageBox.Yes)
#        if reply == QMessageBox.Yes:
        self.draw_shape_initial()
        self.draw_shape_action_list.append(Clear_All())

    
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
    
    def show_distance_method(self):
        if self.show_distance:
            self.show_distance = False
        else:
            self.show_distance = True
    
    def draw_rectangle(self):
        if self.rectangle_button.isChecked():
            self.tool_initial()
            self.draw_shape_rectangle = True
            self.rectangle_button.setChecked(True)
        else:
            self.draw_shape_rectangle = False
            self.rectangle_button.setChecked(False)
        
    def show_side_length_method(self):
        if self.show_side_length:
            self.show_side_length = False
        else:
            self.show_side_length = True
    
    def draw_circle(self):
        if self.circle_button.isChecked():
            self.tool_initial()
            self.draw_shape_circle = True
            self.circle_button.setChecked(True)
        else:
            self.draw_shape_circle = False
            self.circle_button.setChecked(False)

    def show_radius_method(self):
        if self.show_radius:
            self.show_radius = False
        else:
            self.show_radius = True
    
    def erase_shape(self):
        if self.eraser_button.isChecked():
            self.tool_initial()
            self.erase = True
            self.eraser_button.setChecked(True)
        else:
            self.erase = False
            self.eraser_button.setChecked(False)
  
#        QMessageBox.information(self, 'Developing...','Eraser functin is developing...')
    
    def choose_base_line(self):
        self.tool_initial()
        self.choosing_base_line = True
        self.setCursor(Qt.PointingHandCursor)
        
    def clear_base_line(self):
        pass
    
    def angle_measurement(self):
        if self.angle_button.isChecked():
            self.start_angle_measurement = True
            self.angle_button.setChecked(True)
            if len(self.base_line) == 0:
                QMessageBox.warning(self, "No Baseline", 'Please select a base '+\
                                    'line as zero degree')
        else:
            self.start_angle_measurement = False
            self.angle_button.setChecked(False) 
#        QMessageBox.information(self, 'Developing...','Angle measurement function '+\
#                                'is developing... ')
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
                if self.CP:
                    background_name = 'crop_x' + str(self.magnification) + '.png'
                else:
                    background_name = 'x' + str(self.magnification) + '.png'
                reply = QMessageBox.information(self, "Save background", 'Do you want to '+\
                                          'save it as "'+background_name+'"',\
                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if reply == QMessageBox.Yes:    
                    bk_savename = self.current_bk_dir + background_name
                    print(bk_savename)
                    cv2.imwrite(bk_savename, self.capture_bk_average)
                else:
                    bk_savename = QFileDialog.getSaveFileName(self,'save bk',\
                                                self.current_bk_dir,\
                                                "Image files(*.jpg *.png *.bmp)")
                    if bk_savename[0]:
                        cv2.imwrite(bk_savename[0], self.capture_bk_average)
        self.capture_bk_frame.append(self.img_raw)
        self.capture_num += 1
        self.progress_bar.progress = self.capture_num
        
    
    def contact(self):
        QMessageBox.information(self, 'contact','Please contact jingxuxie@berkeley.edu '+\
                                'to report bugs and support feedback. Thanks!')
    
    def about(self):
        QMessageBox.information(self, 'About', 'Camera Tool v3.0. with layer search integrated. '+ \
                                'Proudly designed and created by Jingxu Xie(谢京旭).\n \n'
                                'Copyright © 2019-2020 Jingxu Xie. All Rights Reserved.')
        
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
        fname = QFileDialog.getExistingDirectory(self, 'Set saving folder', self.release_folder)
        if len(fname) != 0:
            try:
                with open(self.current_dir+'saveto.txt','w') as f:
                    f.write(fname)
            except:
                QMessageBox.critical(self, "Missing file", 'The supporting saveto.txt '
                                  'file is missing. Path not set')
            else:
                self.release_folder = fname
                if len(self.release_folder) > 20:
                    self.release_folder_lbl.setText('...'+self.release_folder[-20:])
                else:
                    self.release_folder_lbl.setText(self.release_folder)
    
    def set_magnification(self, text):
        
        self.magnification = int(text[:-1])
        if self.CP:
            self.bk_filename = self.current_bk_dir+'crop_x'+\
                                     str(self.magnification)+'.png'
        else:
            self.bk_filename = self.current_bk_dir+'x'+\
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
        
        self.eraser_button.setChecked(False)
        self.erase = False
        self.drawing_eraser = False
        
        self.choosing_base_line = False
        self.setCursor(Qt.ArrowCursor)
        
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
        lim_x1 = self.lbl_main.x()
        lim_x2 = lim_x1 + self.lbl_main.width()
        lim_y1 = self.lbl_main.y()
        lim_y2 = lim_y1 + self.lbl_main.height() + 50
        if lim_x1 < event.pos().x() < lim_x2 and lim_y1 < event.pos().y() < lim_y2:
#        if not self.combo_mag.underMouse():    
            self.mouse_x1 = max(0, event.pos().x())
            self.mouse_y1 = max(0, event.pos().y())
            self.mouse_x2 = self.mouse_x1 
            self.mouse_y2 = self.mouse_y1
        
            if event.buttons() == Qt.LeftButton and self.zoom_draw and self.zoom_draw_able:
                self.mouse_pos_correct_rec()
                self.zoom_draw_start = True
                    
            elif event.buttons() == Qt.LeftButton and self.DT:
                self.mouse_pos_correct_line()
                self.DT_Line = Line(self.mouse_line_x1, self.mouse_line_y1, \
                                    self.mouse_line_x2, self.mouse_line_y2)
                self.DT_draw = True
                
            elif event.buttons() == Qt.LeftButton and self.CT:
                self.mouse_pos_correct_line()
                self.line_num = len(self.contrast_line)
                if len(self.contrast_line) < 2:
                    self.contrast_line.append(Line(self.mouse_line_x1, self.mouse_line_y1, \
                                                   self.mouse_line_x2, self.mouse_line_y2))
                else:
                    self.contrast_line=[]
                    self.contrast_line.append(Line(self.mouse_line_x1, self.mouse_line_y1, \
                                                   self.mouse_line_x2, self.mouse_line_y2))
                    self.line_num = 0
                self.CT_draw = True
            
            elif event.buttons() == Qt.LeftButton and self.draw_shape_line:
                self.mouse_pos_correct_line()
                self.draw_shape_action_list.append(Line(self.mouse_line_x1, self.mouse_line_y1, \
                                                        self.mouse_line_x2, self.mouse_line_y2, \
                                                        num = self.draw_shape_count,\
                                                        show_distance = self.show_distance))
                self.draw_shape_count += 1
                self.drawing_shape_line = True
                self.undo_redo_setting()
            
            elif event.buttons() == Qt.LeftButton and self.draw_shape_rectangle:
                self.mouse_pos_correct_line()
                self.draw_shape_action_list.append(Rectangle(self.mouse_line_x1, self.mouse_line_y1,\
                                                             self.mouse_line_x2, self.mouse_line_y2,\
                                                             num = self.draw_shape_count,\
                                                             show_side_length = self.show_side_length))
                self.draw_shape_count += 1
                self.drawing_shape_rectangle = True
                self.undo_redo_setting()
                
            elif event.buttons() == Qt.LeftButton and self.draw_shape_circle:
                self.mouse_pos_correct_line()
                self.draw_shape_action_list.append(Circle(self.mouse_line_x1, self.mouse_line_y1,\
                                                          self.mouse_line_x2, self.mouse_line_y2,\
                                                          num = self.draw_shape_count,\
                                                          show_radius = self.show_radius))
                self.draw_shape_count += 1
                self.drawing_shape_circle = True
                self.undo_redo_setting()
                
            elif event.buttons() == Qt.LeftButton and self.erase:
                self.mouse_pos_correct_line()
    #            self.eraser = Eraser(self.mouse_line_x1, self.mouse_line_y1)
                self.draw_shape_action_list.append(Eraser(self.mouse_line_x1, \
                                                          self.mouse_line_y1, num = [0]))
                
                self.drawing_eraser = True
            
            if event.buttons() == Qt.LeftButton and self.choosing_base_line:
                self.mouse_pos_correct_line()
                temp = Point(self.mouse_line_x1, self.mouse_line_y1)
                temp.x1_show, temp.y1_show = self.mouse_pos_ratio_change_line(Shape = temp)
                x_temp, y_temp = Pos_in_Circle(temp.x1_show, temp.y1_show, r = 7 )
                
                for i in range(len(x_temp)):
                    if 0 <= x_temp[i] < self.canvas_blank.shape[1] and 0 <= y_temp[i] < self.canvas_blank.shape[0]:
                        num = self.canvas_blank[y_temp[i], x_temp[i]]
                        if num != 0:
                            for j in range(len(self.draw_shape_list)):
                                if len(self.base_line) != 0:
                                    if self.draw_shape_list[j].prop == 'base line': #and \
                                    #self.draw_shape_list[j].num != num:  
                                        self.draw_shape_list[j].color = copy.deepcopy(self.base_line[0].color)
                                        self.draw_shape_list[j].width = copy.deepcopy(self.base_line[0].width)
                                        self.draw_shape_list[j].prop = copy.deepcopy(self.base_line[0].prop)
                                        #print(self.draw_shape_list[j].color)
                                        break
                            for j in range(len(self.draw_shape_list)):
                                if self.draw_shape_list[j].prop == 'line' and \
                                self.draw_shape_list[j].num == num:
                                    self.base_line = [copy.deepcopy(self.draw_shape_list[j])]
                                    self.draw_shape_list[j].color = (255,255,0)
                                    self.draw_shape_list[j].width = 2
                                    self.draw_shape_list[j].prop = 'base line'
                                    break
                            break
            
            elif event.buttons() == Qt.RightButton:
                if self.zoomed:
                    self.tool_initial()
                    self.zoom_draw = True
                    self.zoom_in_button.setChecked(True)
                    self.zoomed = False
                    self.zoom_draw_able = True
    
    
    def mouseMoveEvent(self, event):
        lim_x1 = self.lbl_main.x()
        lim_x2 = lim_x1 + self.lbl_main.width()
        lim_y1 = self.lbl_main.y()
        lim_y2 = lim_y1 + self.lbl_main.height() + 50
        if lim_x1 < event.pos().x() < lim_x2 and lim_y1 < event.pos().y() < lim_y2:
#        if not self.combo_mag.underMouse():    
            self.mouse_x2 = max(0, event.pos().x())
            self.mouse_y2 = max(0, event.pos().y())
        
            if self.zoom_draw and self.zoom_draw_able:
                self.mouse_pos_correct_rec()
                
            if self.DT_draw:        
                self.mouse_pos_correct_line()
                self.DT_Line.x2 = self.mouse_line_x2
                self.DT_Line.y2 = self.mouse_line_y2
            
            if self.CT_draw:
                self.mouse_pos_correct_line()
                self.contrast_line[-1].x2 = self.mouse_line_x2
                self.contrast_line[-1].y2 = self.mouse_line_y2
            
            if self.drawing_shape_line:
                self.mouse_pos_correct_line()
                self.draw_shape_action_list[-1].x2 = self.mouse_line_x2
                self.draw_shape_action_list[-1].y2 = self.mouse_line_y2
#                self.draw_shape_action_list[-1].pos_refresh()
                
            if self.drawing_shape_rectangle:
                self.mouse_pos_correct_line()
                self.draw_shape_action_list[-1].x2 = self.mouse_line_x2
                self.draw_shape_action_list[-1].y2 = self.mouse_line_y2
#                self.draw_shape_action_list[-1].pos_refresh()
                
            if self.drawing_shape_circle:
                self.mouse_pos_correct_line()
                self.draw_shape_action_list[-1].x2 = self.mouse_line_x2
                self.draw_shape_action_list[-1].y2 = self.mouse_line_y2
#                self.draw_shape_action_list[-1].pos_refresh()
                
            if self.drawing_eraser:
                self.mouse_pos_correct_line()
    #            self.eraser.x1 = self.mouse_line_x2
    #            self.eraser.y1 = self.mouse_line_y2
    #            self.eraser.pos_refresh()
                self.draw_shape_action_list[-1].x1 = self.mouse_line_x2
                self.draw_shape_action_list[-1].y1 = self.mouse_line_y2
#                self.draw_shape_action_list[-1].pos_refresh()
            
            
            
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
        elif event.button() == Qt.LeftButton and self.drawing_eraser:
            self.drawing_eraser = False
            if len(self.draw_shape_action_list[-1].num) == 1:
                self.draw_shape_action_list.pop()
        if event.button() == Qt.LeftButton and self.choosing_base_line:
            pass
#            self.choosing_base_line = False
#            self.setCursor(Qt.ArrowCursor)


    def mouse_pos_correct_line(self):
        self.img_bfDT_width = self.img_show.shape[1]
        self.img_bfDT_height = self.img_show.shape[0]
            
        self.mouse_line_x1, self.mouse_line_x2, \
        self.mouse_line_y1, self.mouse_line_y2 \
        = self.mouse_pos_correct((self.mouse_x1), (self.mouse_x2), \
                                 (self.mouse_y1), (self.mouse_y2))
        if self.mouse_line_x1 >= self.img_bfDT_width:
            self.mouse_line_x1 = self.img_bfDT_width -1
            
        if self.mouse_line_x2 >= self.img_bfDT_width:
            self.mouse_line_x2 = self.img_bfDT_width -1
            
        if self.mouse_line_y1 >= self.img_bfDT_height:
            self.mouse_line_y1 = self.img_bfDT_height -1
            
        if self.mouse_line_y2 >= self.img_bfDT_height:
            self.mouse_line_y2 = self.img_bfDT_height -1
        self.mouse_pos_show2raw()
            
    def mouse_pos_show2raw(self):   
        scale = (self.zoom_x2 - self.zoom_x1) / self.img_show.shape[1]
        self.mouse_line_x1 = self.mouse_line_x1 * scale + self.zoom_x1
        self.mouse_line_x2 = self.mouse_line_x2 * scale + self.zoom_x1
        self.mouse_line_y1 = self.mouse_line_y1 * scale + self.zoom_y1
        self.mouse_line_y2 = self.mouse_line_y2 * scale + self.zoom_y1
            
        if self.CP:
            self.mouse_line_x1 += self.img_raw.shape[1] * self.crop_left_rate / (self.crop_right_rate - self.crop_left_rate)
            self.mouse_line_x2 += self.img_raw.shape[1] * self.crop_left_rate / (self.crop_right_rate - self.crop_left_rate)
        
        
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
        
        if abs(self.mouse_rec_x1 - self.mouse_rec_x2) < 4 or abs(self.mouse_rec_y1 - self.mouse_rec_y2) < 4 \
        or self.mouse_rec_x1 >= self.img_atmouse_width or self.mouse_rec_y1 >= self.img_atmouse_height:
            self.mouse_rec_x1, self.mouse_rec_y1 = 0, 0
            self.mouse_rec_x2, self.mouse_rec_y2 = self.img_atmouse_width - 1, self.img_atmouse_height - 1
            return False      
        return True
    
    def mouse_pos_correct(self, x1, x2, y1, y2):
        lbl_main_x = self.lbl_main.pos().x()
        lbl_main_y = self.lbl_main.pos().y() + self.menubar.height() + self.toolbar.height()
        lbl_main_width = self.lbl_main.frameGeometry().width()
        lbl_main_height = self.lbl_main.frameGeometry().height()
        
        img_for_mouse_correct_width = self.img_show.shape[1]
        img_for_mouse_correct_height = self.img_show.shape[0]
        
        x1 -= round(lbl_main_x + lbl_main_width/2 - img_for_mouse_correct_width/2)
        x2 -= round(lbl_main_x + lbl_main_width/2 - img_for_mouse_correct_width/2)
        y1 -= round(lbl_main_y + lbl_main_height/2 - img_for_mouse_correct_height/2)
        y2 -= round(lbl_main_y + lbl_main_height/2 - img_for_mouse_correct_height/2)
        
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = max(0, x2)
        y2 = max(0, y2)
        
        return copy.copy(x1), copy.copy(x2), copy.copy(y1), copy.copy(y2)
    
    def is_Crop(self, state):
        if not self.zoomed:
            if state == Qt.Checked:
                self.CP = True
                self.bk_filename = self.current_bk_dir+'crop_x'+\
                                     str(self.magnification)+'.png'
            else:
                self.CP = False 
                self.bk_filename = self.current_bk_dir+'x'+\
                                     str(self.magnification)+'.png'
            
            self.get_bk_normalization()
        else:
            QMessageBox.information(self, 'Crop failed','You must exit '
                                'zoom-in mode before cropping. Click right '
                                'button or click zoom-in icon in toolbar to exit.')
    
    def is_SB(self, state):
        if state == Qt.Checked:
            if self.CP:
                self.bk_filename = self.current_bk_dir+'crop_x'+\
                                         str(self.magnification)+'.png'
            else:
                self.bk_filename = self.current_bk_dir+'x'+\
                                         str(self.magnification)+'.png'
            self.get_bk_normalization()
            if self.bk_error:
                self.SB = False
                QMessageBox.critical(self,'Error!','Background file not found. Check '+\
                                 'the support_file for missing background files')
            else:
                self.SB = True
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
                                                 "Image files(*.jpg *.png *.bmp)")
        
        if self.fname[0]:
            self.SB = False
            #self.rgb_initialize()
            self.background = cv2.imread(self.fname[0])
            self.bk_filename = self.fname[0]
            self.get_bk_normalization()
            self.selectbk_folder = get_folder_from_file(self.fname[0])
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
        
    
    def saveFileDialog(self):
        #self.openfile = False
        save_file_name = QFileDialog.getSaveFileName(self,'save as',\
                                                     self.saveFileDialog_folder,\
                                                     "Image files(*.jpg *.png *.bmp)")
        if  save_file_name[0]:
            self.saveFileDialog_folder = get_folder_from_file(save_file_name[0])
            self.refresh_show()
            self.img_save = cv2.cvtColor(self.img_show, cv2.COLOR_BGR2RGB)
            cv2.imwrite(save_file_name[0], self.img_save)
            self.saveFileDialog_folder = get_folder_from_file(save_file_name[0])

    
    def showFileDialog(self):
        self.fname = QFileDialog.getOpenFileName(self, 'Open file',\
                                                 self.showFileDialog_folder,\
                                                 "Image files(*.jpg *.png *.bmp)")
        #加上判断文件类型的操作，试试try except
        if self.fname[0]:
            self.showFileDialog_folder = get_folder_from_file(self.fname[0])
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
    
    def release_sound(self):
        self.sound = QSound(self.current_dir + 'shutter_sound.wav', self)
        self.sound.play()      
    
    def update_release(self):
        self.release_sound()
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
            while os.path.isfile(self.release_folder+'/'+self.date+'-'+str(self.release_count)+'.png'):
                self.release_count += 1
            img_release_temp.append(self.img_raw)
        img_release = img_release_temp[0].astype(int)
        for img in img_release_temp[1:]:
            img_release += img.astype(int)
        #print(len(img_release_temp))
        img_release = img_release / len(img_release_temp)
        self.img_release = img_release.astype(np.uint8)
        cv2.imwrite(self.release_folder+'/'+self.date+'-'+str(self.release_count)+'.png', self.img_release)
        #cv2.imshow('released', self.img_release)
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
            self.left_crop = int(round(self.img_show.shape[1]*self.crop_left_rate))
            self.right_crop = int(round(self.img_show.shape[1]*self.crop_right_rate))
            self.img_show = self.img_show[:, self.left_crop:self.right_crop]
            #self.display_resize()
            self.img_show = np.require(self.img_show, np.uint8, 'C')
            self.display_resize()
            self.left_crop_raw = int(round(self.img_raw.shape[1]*0.17))
            self.right_crop_raw = int(round(self.img_raw.shape[1]*0.83))  
            self.img_raw = self.img_raw[:, self.left_crop_raw: self.right_crop_raw]

        
        self.zoom_x1, self.zoom_y1 = 0, 0
        self.zoom_x2, self.zoom_y2 = self.img_raw.shape[1]-1, self.img_raw.shape[0]-1
        if self.zoom_draw_start:
            cv2.rectangle(self.img_show,(self.mouse_rec_x1,self.mouse_rec_y1),\
                          (self.mouse_rec_x2, self.mouse_rec_y2),(0,0,255),2)
        elif self.zoomed:
            #self.mouse_pos_ratio_change_rec()
            scale_ratio = self.img_raw.shape[1]/self.img_bfzoom_width
            
            self.zoom_y1, self.zoom_y2 = self.mouse_rec_y1*scale_ratio, self.mouse_rec_y2*scale_ratio
            self.zoom_x1, self.zoom_x2 = self.mouse_rec_x1*scale_ratio, self.mouse_rec_x2*scale_ratio

            self.img_show = self.img_raw[int(round(self.zoom_y1)): max(int(round(self.zoom_y2)), int(round(self.zoom_y1)) + 1),\
                                         int(round(self.zoom_x1)): max(int(round(self.zoom_x2)), int(round(self.zoom_x1)) + 1)]
            #print(self.img_show.shape[0],self.img_show.shape[1])
            self.img_show = np.require(self.img_show, np.uint8, 'C')
#            kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], np.float32) #锐化
#            self.img_show = cv2.filter2D(self.img_show, -1, kernel=kernel)
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
            if len(self.img_show.shape) == 3:
                self.img_show = cv2.cvtColor(self.img_show,cv2.COLOR_BGR2GRAY)
            self.img_show = self.change_contrast(self.img_show)
        else:
            try:
                self.img_show = cv2.cvtColor(self.img_show,cv2.COLOR_BGR2RGB)
            except:
                pass
            self.img_show = self.change_contrast(self.img_show)
            
        

        if self.DT_draw:
            self.DT_Line.x1_show, self.DT_Line.y1_show, self.DT_Line.x2_show, self.DT_Line.y2_show \
            = self.mouse_pos_ratio_change_line(Shape = self.DT_Line)
            self.DT_Line.pos_refresh()
            #self.mouse_pos_ratio_change_line()
            cv2.line(self.img_show,*self.DT_Line.pos,(255,0,0),2)
            '''
            self.distance = np.sqrt((self.mouse_line_x2-self.mouse_line_x1)**2\
                                    +(self.mouse_line_y2-self.mouse_line_y1)**2)
            self.distance /= self.img_show.shape[0]
            if self.zoomed:
                zoom_ratio = (self.mouse_rec_y2 - self.mouse_rec_y1)/self.img_atmouse_height           
                self.distance *= zoom_ratio
            self.distance = self.distance*1000/self.magnification*self.calibration
            '''
            self.distance = self.calculate_distance(self.DT_Line.x1, self.DT_Line.y1,\
                                                    self.DT_Line.x2, self.DT_Line.y2)
            self.distance_lbl.setText(str(round(self.distance,2))+' um')
            cv2.putText(self.img_show, str(round(self.distance,2)), \
                        (round((self.DT_Line.x1_show + self.DT_Line.x2_show)/2),\
                         round((self.DT_Line.y1_show + self.DT_Line.y2_show)/2)),self.font,\
                         0.7, (255,0,0), 1, cv2.LINE_AA)
        if self.CT_draw:
            if len(self.contrast_line) == 2:
                for line in self.contrast_line:
                    line.x1_show, line.y1_show, line.x2_show, line.y2_show \
                        = self.mouse_pos_ratio_change_line(Shape = line)
                    
                    line.pos_refresh()
                
                
                self.contrast \
                = calculate_contrast(self.img_show,\
                   self.contrast_line[0].x1_show, self.contrast_line[0].y1_show,\
                   self.contrast_line[0].x2_show, self.contrast_line[0].y2_show,\
                   self.contrast_line[1].x1_show, self.contrast_line[1].y1_show,\
                   self.contrast_line[1].x2_show, self.contrast_line[1].y2_show)
                #for i in range(len(xtemp)):
                 #   cv2.circle(self.img_show,(xtemp[i],ytemp[i]),1,(0,0,255))
                
                #self.contrast = 0
                cv2.putText(self.img_show, str(round(self.contrast,4)), \
                        (round((self.contrast_line[1].x1_show + self.contrast_line[1].x2_show)/2),\
                         round((self.contrast_line[1].y1_show + self.contrast_line[1].y2_show)/2)),self.font,\
                         0.7, (255,0,0), 1, cv2.LINE_AA)
            else:
                self.contrast = 0
            self.contrast_lbl.setText(str(round(self.contrast,4)))
            for line in self.contrast_line:
                line.x1_show, line.y1_show, line.x2_show, line.y2_show \
                    = self.mouse_pos_ratio_change_line(Shape = line)
                line.pos_refresh()
                
                cv2.line(self.img_show, *line.pos, (255,0,0),2)
        
        if self.drawing_eraser:
            eraser_temp = self.draw_shape_action_list[-1]
            eraser_temp.x1_show, eraser_temp.y1_show \
            = self.mouse_pos_ratio_change_line(Shape = eraser_temp)
            eraser_temp.pos_refresh()
            cv2.circle(self.img_show, *eraser_temp.pos, eraser_temp.size, \
                       eraser_temp.color, eraser_temp.width)
            cv2.circle(self.img_show, *eraser_temp.pos, eraser_temp.size, \
                       (100,100,100), 2)
            self.find_eraser_num()
        if len(self.draw_shape_action_list) > 0:
            self.generate_draw_shape_list()
            self.draw_shape_canvas()        
        if self.start_angle_measurement:
            self.show_angle_value()
        if self.show_scale:
            self.draw_graduated_scale()
        
#        self.mouse_pos_ratio_change_done()
    
    
    
    def draw_graduated_scale(self):
        scale_for_raw = max(1, self.img_show.shape[0]/1000)
        scale = (self.zoom_x2 - self.zoom_x1) / self.img_show.shape[1]
        img_width = self.img_show.shape[1]
        img_height = self.img_show.shape[0]
        width = self.calculate_distance(0, img_width * scale, 0, 0)
        height = self.calculate_distance(0, img_height * scale, 0, 0)
        dimension = max(width, height)
        if dimension > 2000:
            unit = 400
        elif dimension > 1000:
            unit = 200
        elif dimension > 500:
            unit = 100
        elif dimension > 200:
            unit = 40
        elif dimension >100:
            unit = 20
        elif dimension > 50:
            unit = 10
        else:
            unit = 5
        standard_D = self.calculate_distance(0, 1000*scale, 0, 0)
        unit_for_img = round(unit/standard_D*1000).astype(int)
        cv2.line(self.img_show, (0, int(2*scale_for_raw)), (img_width, int(2*scale_for_raw)), (255, 0, 0), int(3*scale_for_raw))
        cv2.line(self.img_show, (int(2*scale_for_raw), 0), (int(2*scale_for_raw), img_height), (255, 0, 0), int(3*scale_for_raw))
        
        scale_for_img = unit_for_img
        scale_for_text = unit
        cv2.putText(self.img_show, str(self.magnification)+'x', (int(5*scale_for_raw), int(25*scale_for_raw)),self.font, 0.7*scale_for_raw, (255,0,0), int(2*scale_for_raw), cv2.LINE_AA)
        while scale_for_img < img_width:
            cv2.line(self.img_show, (scale_for_img, 0), (scale_for_img, int(15*scale_for_raw)), (255,0,0), int(2*scale_for_raw))
            text = str(scale_for_text)
            cv2.putText(self.img_show, text, (scale_for_img-int(15*scale_for_raw), int(30*scale_for_raw)), self.font, 0.5*scale_for_raw,(255,0,0),\
                        int(1*scale_for_raw), cv2.LINE_AA)
            scale_for_img += unit_for_img
            scale_for_text += unit
        
        scale_for_img = unit_for_img
        scale_for_text = unit
        while scale_for_img < img_height:
            cv2.line(self.img_show, (0, scale_for_img), (int(15*scale_for_raw), scale_for_img), (255,0,0), int(2*scale_for_raw))
            text = str(scale_for_text)
            cv2.putText(self.img_show, text, (int(5*scale_for_raw), scale_for_img-int(5*scale_for_raw)), self.font, 0.5*scale_for_raw, (255,0,0),\
                        int(1*scale_for_raw), cv2.LINE_AA)
            scale_for_img += unit_for_img
            scale_for_text += unit
    
    
    def calculate_distance(self, x1, y1, x2, y2):
        distance = np.sqrt((x2-x1)**2+(y2-y1)**2)
        distance /= self.img_raw.shape[0]
#        if self.CP:
#            distance *= 1/(self.crop_right_rate - self.crop_left_rate)
        distance = distance*1000/self.magnification*self.calibration
        return distance
    
    def show_angle_value(self):
        if len(self.base_line) == 0:
            return False
        else:
            i = 0
            while i < len(self.draw_shape_list):
                if self.draw_shape_list[i].num == self.base_line[0].num:
                    break
                i += 1
            if i == len(self.draw_shape_list):
                self.base_line = []
            else:
                for shape in self.draw_shape_list:
                    if shape.prop == 'line' or shape.prop == 'base line':
                        angle = calculate_angle((self.base_line[0].x1, self.base_line[0].y1), \
                                                (self.base_line[0].x2, self.base_line[0].y2), \
                                                (shape.x1, shape.y1),\
                                                (shape.x2, shape.y2))
                        cv2.putText(self.img_show, str(round(angle,2)), shape.pos[1], \
                                    self.font, 0.7, (255,0,0), 2, cv2.LINE_AA)
                
                
    
    
    def generate_draw_shape_list(self):
        self.draw_shape_list = []
        for action in self.draw_shape_action_list:
            if action.prop != 'eraser' and action.prop != 'clear':
                self.draw_shape_list.append(action)
            elif action.prop == 'eraser':
                i = 0
                while i < len(self.draw_shape_list):
                    if self.draw_shape_list[i].num in action.num:
                        #print(action.num)
                        self.draw_shape_list.pop(i)
                        i -= 1
                    i += 1
                    if i == len(self.draw_shape_list):
                        break
            elif action.prop == 'clear':
                self.draw_shape_list = []
                
                
    def find_eraser_num(self):
        x_temp, y_temp = Pos_in_Circle(*list(self.draw_shape_action_list[-1].pos[0]), \
                                       self.draw_shape_action_list[-1].size)
        for i in range(len(x_temp)):
            if 0 <= x_temp[i] < self.canvas_blank.shape[1] and 0 <= y_temp[i] < self.canvas_blank.shape[0]:
                num = self.canvas_blank[y_temp[i], x_temp[i]]
                if num != 0:
                    self.draw_shape_action_list[-1].num.append(num)
                    break
           
                    
        
    def draw_shape_canvas(self):
        #目前canvas还没什么用，均可用img_show代替，但也可以先留着
        self.canvas = np.zeros(self.img_show.shape, dtype = np.uint8)
        self.canvas_blank = np.zeros((self.img_show.shape[0], self.img_show.shape[1]), dtype = int)   
        if len(self.draw_shape_list) == 0:
            pass
        for shape in self.draw_shape_list:
            shape.x1_show, shape.y1_show, shape.x2_show, shape.y2_show \
            = self.mouse_pos_ratio_change_line(Shape = shape)
            
#            shape.x2, shape.y2 = self.mouse_pos_ratio_change_line(shape.x2, shape.y2)
            shape.pos_refresh()
            if shape.prop == 'line' or shape.prop == 'base line':
                x_temp, y_temp = Pos_of_Line(*list(shape.pos[0]), *list(shape.pos[1]))
                self.canvas_blank = record_draw_shape(self.canvas_blank, \
                                                      np.array(x_temp), np.array(y_temp), \
                                                      shape.num)
                cv2.line(self.img_show, *shape.pos, shape.color, shape.width)
                if shape.show_distance:
                    distance = self.calculate_distance(shape.x1, shape.y1, \
                                                       shape.x2, shape.y2)
                    pos = (int((shape.x1_show + shape.x2_show)/2), \
                           int((shape.y1_show + shape.y2_show)/2))
                    cv2.putText(self.img_show, str(round(distance, 2)), pos, \
                                self.font, 0.7, (255,0,0), 1, cv2.LINE_AA)
                
            elif shape.prop == 'rec':
                x_temp, y_temp = Pos_of_Rec(*list(shape.pos[0]), *list(shape.pos[1]))
                self.canvas_blank = record_draw_shape(self.canvas_blank, \
                                                      x_temp, y_temp, shape.num)
                cv2.rectangle(self.img_show, *shape.pos, shape.color, shape.width)
                if shape.show_side_length:
                    distance1 = self.calculate_distance(shape.x1, shape.y1,\
                                                        shape.x2, shape.y1)
                    distance2 = self.calculate_distance(shape.x1, shape.y1,\
                                                        shape.x1, shape.y2)
                    pos1 = (int((shape.x1_show + shape.x2_show)/2), shape.y1_show)
                    pos2 = (shape.x1_show, int((shape.y1_show + shape.y2_show)/2))
                    cv2.putText(self.img_show, str(round(distance1, 2)), pos1, \
                                self.font, 0.7, (255,0,0), 1, cv2.LINE_AA)
                    cv2.putText(self.img_show, str(round(distance2, 2)), pos2, \
                                self.font, 0.7, (255,0,0), 1, cv2.LINE_AA)
                    
            elif shape.prop == 'circle':
                x_temp, y_temp = Pos_of_Circle(*list(shape.pos[0]), shape.radius)
                self.canvas_blank = record_draw_shape(self.canvas_blank, \
                                                      x_temp, y_temp, shape.num)
                cv2.circle(self.img_show, *shape.pos, shape.radius_show, shape.color, shape.width)
                if shape.show_radius:
                    radius = self.calculate_distance(shape.center_x, shape.center_y,\
                                                     shape.x2, shape.y2)
                    pos = (int((shape.center_x_show + shape.x2_show)/2), int((shape.center_y_show + shape.y2_show)/2))
                    cv2.line(self.img_show, (shape.center_x_show, shape.center_y_show), (shape.x2_show, shape.y2_show),\
                             (255,0,0),1)
                    cv2.putText(self.img_show, str(round(radius, 2)), pos, \
                                self.font, 0.7, (255,0,0), 1, cv2.LINE_AA)
        
        #self.add_canvas_to_show()


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
    
#    def mouse_pos_ratio_change_line(self):
#        if self.img_bfDT_width != self.resize_show_width:
#            self.mouse_line_x1 = int(self.mouse_line_x1/self.img_bfDT_width*\
#                                   self.resize_show_width)
#            self.mouse_line_x2 = int(self.mouse_line_x2/self.img_bfDT_width*\
#                                   self.resize_show_width)
#            self.img_bfDT_width = self.resize_show_width
#        if self.img_bfDT_height != self.resize_show_height:
#            self.mouse_line_y1 = int(self.mouse_line_y1/self.img_bfDT_height*\
#                                   self.resize_show_height)
#            self.mouse_line_y2 = int(self.mouse_line_y2/self.img_bfDT_height*\
#                                   self.resize_show_height)
#            self.img_bfDT_height = self.resize_show_height
    
    def mouse_pos_ratio_change_line(self, Shape = None):
#        if self.CP:
#            self.zoom_x2 = self.img_raw.shape[1] * self.crop_right_rate
#            self.zoom_x1 = self.img_raw.shape[1] * self.
        
        scaled_width = 1 / (self.zoom_x2 - self.zoom_x1) * self.img_raw.shape[1] * self.img_show.shape[1]
        
        x_start = self.zoom_x1 / self.img_raw.shape[1] * scaled_width
        y_start = self.zoom_y1 / self.img_raw.shape[1] * scaled_width
        
        x_crop = 0
        if self.CP:
            x_crop = self.img_raw.shape[1] * self.crop_left_rate / (self.crop_right_rate-self.crop_left_rate)
        
        
        if Shape:
            x1 = int(round((Shape.x1 - x_crop) / self.img_raw.shape[1] * scaled_width - x_start))
            y1 = int(round(Shape.y1 / self.img_raw.shape[1] * scaled_width - y_start))
            
            
            if Shape.prop == 'eraser' or Shape.prop == 'point':
                return x1, y1
            
            x2 = int(round((Shape.x2 - x_crop) / self.img_raw.shape[1] * scaled_width - x_start))
            y2 = int(round(Shape.y2 / self.img_raw.shape[1] * scaled_width - y_start))
#            if self.CP:
#                x2 -= int(self.img_show.shape[1] * self.crop_left_rate / (self.crop_right_rate-self.crop_left_rate))
            
            return x1, y1, x2, y2
                    
            
    def mouse_pos_ratio_change_done(self):
        self.img_bfDT_width = self.resize_show_width
        self.img_bfDT_height = self.resize_show_height

    def show_on_screen(self):
        self.img_qi = self.np2qimage(self.img_show)
        self.pixmap = QPixmap(self.img_qi)
        self.lbl_main.setPixmap(self.pixmap)
        self.draw_hist()
        if self.window_normal:
            self.resize(self.initial_window_width, self.initial_window_height)
            #print(self.geometry().width(),self.initial_window_width)
            #print(self.geometry().height(),self.initial_window_height)
            if self.geometry().width() == self.initial_window_width and \
                self.geometry().height() == self.initial_window_height + 12:
#                print(self.frameGeometry().height() - self.geometry().height())
                self.window_normal = False
    
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
        if self.show_scale:
            self.img_raw = cv2.cvtColor(self.img_raw, cv2.COLOR_BGR2RGB)
            self.img_show = self.img_raw
            self.draw_graduated_scale()
            self.img_raw = cv2.cvtColor(self.img_show, cv2.COLOR_RGB2BGR)
        if len(self.draw_shape_action_list) > 0:
            self.generate_draw_shape_list()
            self.img_raw = cv2.cvtColor(self.img_raw, cv2.COLOR_BGR2RGB)
            self.draw_shape_canvas_for_raw()
            self.img_raw = cv2.cvtColor(self.img_raw, cv2.COLOR_RGB2BGR)
            
    def draw_shape_canvas_for_raw(self):
        if len(self.draw_shape_list) == 0:
            return
        if self.openfile:
            temp = self.img_raw_not_cropped
        else:
            temp = self.camera.last_frame
        self.canvas_raw = np.zeros(temp.shape, dtype = np.uint8)
        scale = max(1, self.canvas_raw.shape[0] / 1000)
        for shape in self.draw_shape_list:
            if shape.prop == 'line' or shape.prop == 'base line':
                cv2.line(self.canvas_raw, (int(shape.x1), int(shape.y1)), (int(shape.x2), int(shape.y2)), shape.color, int(shape.width*scale))
                if shape.show_distance:
                    distance = self.calculate_distance(shape.x1, shape.y1, \
                                                       shape.x2, shape.y2)
                    pos = (int((shape.x1 + shape.x2)/2), \
                           int((shape.y1 + shape.y2)/2))
                    cv2.putText(self.canvas_raw, str(round(distance, 2)), pos, \
                                self.font, 0.7*scale, (255,0,0), int(1*scale), cv2.LINE_AA)
                
            elif shape.prop == 'rec':
                cv2.rectangle(self.canvas_raw, (int(shape.x1), int(shape.y1)), (int(shape.x2), int(shape.y2)), shape.color, int(shape.width*scale))
                if shape.show_side_length:
                    distance1 = self.calculate_distance(shape.x1, shape.y1,\
                                                        shape.x2, shape.y1)
                    distance2 = self.calculate_distance(shape.x1, shape.y1,\
                                                        shape.x1, shape.y2)
                    pos1 = (int((shape.x1 + shape.x2)/2), int(shape.y1))
                    pos2 = (int(shape.x1), int((shape.y1 + shape.y2)/2))
                    cv2.putText(self.canvas_raw, str(round(distance1, 2)), pos1, \
                                self.font, 0.7*scale, (255,0,0), int(1*scale), cv2.LINE_AA)
                    cv2.putText(self.canvas_raw, str(round(distance2, 2)), pos2, \
                                self.font, 0.7*scale, (255,0,0), int(1*scale), cv2.LINE_AA)
                    
            elif shape.prop == 'circle':
                cv2.circle(self.canvas_raw, (shape.center_x, shape.center_y), shape.radius, shape.color, int(shape.width*scale))
                if shape.show_radius:
                    radius = self.calculate_distance(shape.center_x, shape.center_y,\
                                                     shape.x2, shape.y2)
                    pos = (int((shape.center_x + shape.x2)/2), int((shape.center_y + shape.y2)/2))
                    cv2.line(self.canvas_raw, (int(shape.center_x), int(shape.center_y)), (int(shape.x2), int(shape.y2)),\
                             (255,0,0), int(1*scale))
                    cv2.putText(self.canvas_raw, str(round(radius, 2)), pos, \
                                self.font, 0.7*scale, (255,0,0), int(1*scale), cv2.LINE_AA)
        self.add_canvas_to_raw()
    

    def add_canvas_to_raw(self):
        if self.CP:
            self.canvas_raw = self.canvas_raw[:, self.left_crop_raw: self.right_crop_raw]
        canvas_gray = cv2.cvtColor(self.canvas_raw, cv2.COLOR_BGR2GRAY)
        ret, mask = cv2.threshold(canvas_gray, 10, 255, cv2.THRESH_BINARY_INV)
        
        img1_bg = cv2.bitwise_and(self.img_raw, self.img_raw, mask = mask)
       #img2_fg = cv2.bitwise_and(self.canvas,self.canvas,mask = mask)

        self.img_raw = cv2.add(img1_bg, self.canvas_raw)
        
   
    def draw_hist(self):
        counts = [256]
        interval = [0, 256]
        if len(self.img_show.shape) == 3:
            hist_r = cv2.calcHist([self.img_show], [0], None, counts,interval)
            hist_g = cv2.calcHist([self.img_show], [1], None, counts,interval)
            hist_b = cv2.calcHist([self.img_show], [2], None, counts,interval)
            
            hist_r[0] = 0
            hist_g[0] = 0
            hist_b[0] = 0
            
            hist_r = hist_r.reshape(len(hist_r))
            hist_g = hist_g.reshape(len(hist_g))
            hist_b = hist_b.reshape(len(hist_b))
            
            hist_r = hist_r/(max(hist_r)+1)*1000
            hist_g = hist_g/(max(hist_g)+1)*1000
            hist_b = hist_b/(max(hist_b)+1)*1000
            
            self.pw_hist.clear()
            self.pw_hist.plot(hist_r, pen = pg.mkPen(color = 'r', width = 2), fillLevel=1, brush=(255,0,0,200))
            self.pw_hist.plot(hist_g, pen = pg.mkPen(color = 'g', width = 2), fillLevel=1, brush=(0,200,0,150))
            self.pw_hist.plot(hist_b, pen = pg.mkPen(color = 'b', width = 3), fillLevel=1, brush=(100,100,255,150))
        else:
            hist_gray = cv2.calcHist([self.img_show], [0], None, counts,interval)
            hist_gray[0] = 0
            hist_gray = hist_gray.reshape(len(hist_gray))
            hist_gray = hist_gray/(max(hist_gray)+1)*1000
            self.pw_hist.clear()
            self.pw_hist.plot(hist_gray, fillLevel=1, brush=(255,255,255,150))
    
    
    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if self.windowState() & Qt.WindowMaximized:
                self.window_normal = False
                self.window_width = self.geometry().width()
                self.window_height = self.geometry().height()

            else:
                self.window_normal = True
                self.window_width = self.initial_window_width
                self.window_height = self.initial_window_height
            
           
    def display_resize(self):
        if self.window_normal:
            self.window_width = self.initial_window_width
            self.window_height = self.initial_window_height
        else:
            self.window_width = self.geometry().width()
            self.window_height = self.geometry().height()
        
        self.img_show_width = max(1, self.img_show.shape[1])
        self.img_show_height = max(1, self.img_show.shape[0])       
        self.scale_rate = min((self.window_width-300)/self.img_show_width, \
                              (self.window_height-125)/self.img_show_height)        
        self.resize_show_width = round(self.img_show_width*self.scale_rate)
        self.resize_show_height = round(self.img_show_height*self.scale_rate)
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
    
    
    app = QApplication(sys.argv)
    
    splash = QSplashScreen(QPixmap('F:/Desktop2019.8.15/SonyView/support_file/shutter.jpg'))
    splash.show()
    splash.showMessage('Loading……')
    
    camera = Camera(0)
    camera.initialize()
    
    
    #slid = MainWindow(camera)
    line = LineEdit()
    line.show()
    splash.close()
    sys.exit(app.exec_())
    
    camera.close_camera()
    
    
    
    
    
