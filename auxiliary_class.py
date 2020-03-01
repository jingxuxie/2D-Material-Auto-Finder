# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 20:52:59 2020

@author: HP
"""
import numpy as np
from PyQt5.QtWidgets import QWidget, QSlider, QVBoxLayout, QHBoxLayout, \
    QLabel, QGridLayout, QProgressBar, QDesktopWidget, QLineEdit, QShortcut,\
    QPushButton, QComboBox, QMessageBox
    
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal

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



class CameraNumEdit(QWidget):
    def __init__(self, current_num = 0):
        super().__init__()
        self.current_num = current_num
        self.camera_num = current_num
        self.init_ui()
        
    def init_ui(self):
        label_current = QLabel(self)
        label_current.setText('Current number')
        label_current_value = QLabel(self)
        label_current_value.setText(str(self.current_num))
        
        label_new = QLabel(self)
        label_new.setText('New number')
        self.line_edit = QLineEdit(self)
        
        self.con_but_click_num = 0
        
        self.save_later_button = QPushButton('Save for later', self)
        self.save_later_button.clicked.connect(self.save)
        
        self.save_once_button = QPushButton('Save for once', self)
        self.save_once_button.clicked.connect(self.save)
        
        for sequence in ("Enter", "Return",):
            shorcut = QShortcut(sequence, self.save_once_button)
            shorcut.activated.connect(self.save_once_button.animateClick)
        
        cancel_button = QPushButton('Cancel', self)
        cancel_button.clicked.connect(self.cancel)
        
        hbox1 = QHBoxLayout()
        hbox1.addWidget(label_current)
        hbox1.addWidget(label_current_value)
        
        hbox2 = QHBoxLayout()
        hbox2.addWidget(label_new)
        hbox2.addWidget(self.line_edit)
        
        hbox3 = QHBoxLayout()
        hbox3.addWidget(self.save_later_button)
        hbox3.addWidget(self.save_once_button)
        hbox3.addWidget(cancel_button)
        
        vbox = QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)

        self.setLayout(vbox)
        self.setWindowTitle('Setting Camera Number')
    
    def save(self):
        self.camera_num = self.line_edit.text()
    
    def cancel(self):
        self.close()



class CalibrationEdit(QWidget):
    def __init__(self, current_calibration):
        super().__init__()
        self.current_calibration = current_calibration
        self.calibration = current_calibration
        self.init_ui()
        
    def init_ui(self):
#        label_default = QLabel(self)
#        label_default.setText('Default calibration')
#        label_default_value = QLabel(self)
#        label_default_value.setText('14.33')
        
        label_current = QLabel(self)
        label_current.setText('Current calibration: ')
        label_current_value = QLabel(self)
        label_current_value.setText(str(self.current_calibration))
        
        label_set = QLabel(self)
        label_set.setText('New calibration: ')
        self.line_edit = QLineEdit(self)
        
        self.con_but_click_num = 0
        
        self.save_later_button = QPushButton('Save for later', self)
        self.save_later_button.clicked.connect(self.save_later)
        
        self.save_once_button = QPushButton('Save for once', self)
        self.save_once_button.clicked.connect(self.save_once)
        
        for sequence in ("Enter", "Return",):
            shorcut = QShortcut(sequence, self.save_once_button)
            shorcut.activated.connect(self.save_once_button.animateClick)
        
        cancel_button = QPushButton('Cancel', self)
        cancel_button.clicked.connect(self.cancel)
        
        hbox1 = QHBoxLayout()
        hbox1.addWidget(label_current)
        hbox1.addWidget(label_current_value)
        
        hbox2 = QHBoxLayout()
        hbox2.addWidget(label_set)
        hbox2.addWidget(self.line_edit)
        
        hbox3 = QHBoxLayout()
        hbox3.addWidget(self.save_later_button)
        hbox3.addWidget(self.save_once_button)
        hbox3.addWidget(cancel_button)
        
        vbox = QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)

        self.setLayout(vbox)
        self.setWindowTitle('Setting Calibration')
    
    def save_later(self):
        self.calibration = self.line_edit.text()
    
    def save_once(self):
        self.calibration = self.line_edit.text()
        if self.con_but_click_num == 0:
            self.con_but_click_num += 1
           
    def cancel(self):
        self.close()
        
        
        
        
class ThicknessChoose(QWidget):
    confirmed = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        label_material = QLabel(self)
        label_material.setText('Material')
        
        label_thickness = QLabel(self)
        label_thickness.setText('Thickness')
        
        self.combo_material = QComboBox(self)
        self.combo_material.addItem('graphene')
        self.combo_material.addItem('TMD')
        self.material = self.combo_material.currentText()
        
        self.combo_thickness = QComboBox(self)
        self.combo_thickness.addItem('285nm')
        self.combo_thickness.addItem('90nm')
        self.thickness = self.combo_thickness.currentText()
        
        self.con_but_click_num = 0
        confirm_button = QPushButton('Confirm', self)
        confirm_button.clicked.connect(self.confirm)
        for sequence in ("Enter", "Return",):
            shorcut = QShortcut(sequence, confirm_button)
            shorcut.activated.connect(confirm_button.animateClick)
        
        cancel_button = QPushButton('Cancel', self)
        cancel_button.clicked.connect(self.cancel)
        
        hbox1 = QHBoxLayout()
        hbox1.addWidget(label_material)
        hbox1.addWidget(self.combo_material)
        
        hbox2 = QHBoxLayout()
        hbox2.addWidget(label_thickness)
        hbox2.addWidget(self.combo_thickness)
        
        hbox3 = QHBoxLayout()
        hbox3.addWidget(confirm_button)
        hbox3.addWidget(cancel_button)
        
        vbox = QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)

        self.setLayout(vbox)
        
    def confirm(self):
        if self.con_but_click_num == 0:
            self.con_but_click_num += 1
            
            self.material = self.combo_material.currentText()
            self.thickness = self.combo_thickness.currentText()
            print(self.material, self.thickness)
            self.confirmed.emit('confirmed')
           
    def cancel(self):
        self.close()
        reply = QMessageBox.warning(self, "Warning", 'Do you want to search with '+\
                                    '285nm substrate?',+\
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            self.thickness_confirm.emit('285nm')
        else:
            reply = QMessageBox.warning(self, "Warning", 'Do you want to stop searching?',+\
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.No:
            self.show()
        
        
        
class SearchingProperty(QWidget):
    confirmed = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        label_material = QLabel(self)
        label_material.setText('Material')
        
        label_thickness = QLabel(self)
        label_thickness.setText('Thickness')
        
        label_mag = QLabel(self)
        label_mag.setText('Mgnification')
        
        self.combo_material = QComboBox(self)
        self.combo_material.addItem('graphene')
        self.combo_material.addItem('TMD')
        self.material = self.combo_material.currentText()
        
        self.combo_thickness = QComboBox(self)
        self.combo_thickness.addItem('285nm')
        self.combo_thickness.addItem('90nm')
        self.thickness = self.combo_thickness.currentText()
        
        self.combo_mag = QComboBox(self)
        self.combo_mag.addItem('5x')
        self.combo_mag.addItem('20x')
        self.magnification = self.combo_mag.currentText()
        
        self.con_but_click_num = 0
        confirm_button = QPushButton('Confirm', self)
        confirm_button.clicked.connect(self.confirm)
        for sequence in ("Enter", "Return",):
            shorcut = QShortcut(sequence, confirm_button)
            shorcut.activated.connect(confirm_button.animateClick)
        
        cancel_button = QPushButton('Cancel', self)
        cancel_button.clicked.connect(self.cancel)
        
        hbox1 = QHBoxLayout()
        hbox1.addWidget(label_material)
        hbox1.addWidget(self.combo_material)
        
        hbox2 = QHBoxLayout()
        hbox2.addWidget(label_thickness)
        hbox2.addWidget(self.combo_thickness)
        
        hbox3 = QHBoxLayout()
        hbox3.addWidget(label_mag)
        hbox3.addWidget(self.combo_mag)
        
        hbox4 = QHBoxLayout()
        hbox4.addWidget(confirm_button)
        hbox4.addWidget(cancel_button)
        
        vbox = QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        vbox.addLayout(hbox4)
        
        self.setLayout(vbox)
        
    def confirm(self):
        if self.con_but_click_num == 0:
            self.con_but_click_num += 1
            
            self.material = self.combo_material.currentText()
            self.thickness = self.combo_thickness.currentText()
            self.magnification = self.combo_mag.currentText()
            print(self.material, self.thickness, self.magnification)
            self.confirmed.emit('confirmed')
            
    def cancel(self):
        self.close()
#        reply = QMessageBox.warning(self, "Warning", 'Do you want to search with '+\
#                                    '285nm substrate?',+\
#                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
#        if reply == QMessageBox.Yes:
#            self.thickness_confirm.emit('285nm')
#        else:
#            reply = QMessageBox.warning(self, "Warning", 'Do you want to stop searching?',+\
#                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
#        if reply == QMessageBox.No:
#            self.show()
            
        
    
    
    