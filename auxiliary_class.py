# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 20:52:59 2020

@author: HP
"""
import numpy as np
from PyQt5.QtWidgets import QWidget, QSlider, QVBoxLayout, QHBoxLayout, \
    QLabel, QGridLayout, QProgressBar, QDesktopWidget, QLineEdit, QShortcut,\
    QPushButton, QComboBox, QMessageBox, QCheckBox, QListWidget, QListWidgetItem
import cv2
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal
from PyQt5.QtGui import QPixmap
from Threads import StageThread
import os
from auxiliary_func import get_folder_from_file, np2qimage


class DropLabel(QLabel):
    new_img = pyqtSignal(str)
    def __init__(self, title, parent):
        super().__init__(title, parent)
        self.setAcceptDrops(True)
        self.support_format = ['jpg', 'JPG', 'png', 'PNG', 'bmp', 'BMP']
        
    def dragEnterEvent(self, e):
        m = e.mimeData()
        if m.hasUrls():
            if m.urls()[0].toLocalFile()[-3:] in self.support_format:
                e.accept()
            else:
                e.ignore()
        else:
            e.ignore()
    
    def dropEvent(self, e):
        m = e.mimeData()
        if m.hasUrls():
            self.img_path = m.urls()[0].toLocalFile()
            self.img = cv2.imread(m.urls()[0].toLocalFile())
            self.new_img.emit('new') 
#            print(m.urls()[0].toLocalFile())
            

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
        
        
class CalibrateCoordinate(QWidget):
    finished_signal = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.stage = StageThread(0)
        
        self.current_dir = os.path.abspath(__file__).replace('\\','/')
        self.current_dir = get_folder_from_file(self.current_dir)
        self.xy_step_file = self.current_dir + 'support_file/coordinate_calibration.txt'
        self.xy_step = np.loadtxt(self.xy_step_file)
        
        self.label = QLabel(self)
        self.label.setText('This tool is for coordinate calibration. Please follow the '+\
                           'instructions and click Next to continue.')
        
#        self.img_1 = cv2.imread(self.current_dir + 'support_file/coordinate_calibration_1.png')
        self.read_img()
        
        self.pixmap = QPixmap(self.img_1_qi)
        
        self.label_image = QLabel(self)
        self.label_image.setPixmap(self.pixmap)
        self.label_image.hide()
        
        self.back_button = QPushButton('Back', self)
        self.back_button.clicked.connect(self.back_action)
        self.back_button.hide()
        
        self.next_button = QPushButton('Next', self)
        self.next_button.clicked.connect(self.next_action)
        self.next_count = 0
        
        self.pos_list = [[0, 0] for i in range(4)]
        
        hbox = QHBoxLayout()
        hbox.addWidget(self.back_button)
        hbox.addStretch(1)
        hbox.addWidget(self.next_button)
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.label)
        vbox.addWidget(self.label_image)
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        self.setWindowTitle('Calibrate coordinates')
        
    def next_action(self):
#        print(self.next_count)
        self.next_count += 1
        self.change_label_text()
        if self.next_count > 4:
            self.finished()
        if 1 < self.next_count < 5:
            self.get_current_pos()
    
    def back_action(self):
        self.next_count -= 1
        if self.next_count == 0:
            self.back_button.hide()
            self.label_image.hide()
            self.label.setText('This tool is for coordinate calibration. Please follow the '+\
                           'instructions and click Next to continue.')
        else:
            self.next_button.setText('Next')
            self.change_label_text()
        
    def change_label_text(self):
        if self.next_count == 1:
            self.back_button.show()
            self.label.setText('Please move to the bottom right corner, then click Next')
            self.pixmap = QPixmap(self.img_1_qi)
            self.label_image.setPixmap(self.pixmap)
            self.label_image.show()
        elif self.next_count == 2:
            self.label.setText('Please move leftward, then click Next')
            self.pixmap = QPixmap(self.img_2_qi)
            self.label_image.setPixmap(self.pixmap)
        elif self.next_count == 3:
            self.label.setText('please move backward, then click Next')
            self.pixmap = QPixmap(self.img_3_qi)
            self.label_image.setPixmap(self.pixmap)
            self.label_image.show()
        elif self.next_count == 4:
            self.label_image.hide()
            self.label.setText('Done!')
            self.next_button.setText('Finish')
        else:
            pass
    
    def read_img(self):
        img_1 = cv2.imread(self.current_dir + 'support_file/coordinate_calibration_1.png')
        img_1 = cv2.cvtColor(img_1, cv2.COLOR_BGR2RGB)
        img_2 = cv2.imread(self.current_dir + 'support_file/coordinate_calibration_2.png')
        img_2 = cv2.cvtColor(img_2, cv2.COLOR_BGR2RGB)
        img_3 = cv2.imread(self.current_dir + 'support_file/coordinate_calibration_3.png')
        img_3 = cv2.cvtColor(img_3, cv2.COLOR_BGR2RGB)
        self.img_1_qi = np2qimage(img_1)
        self.img_2_qi = np2qimage(img_2)
        self.img_3_qi = np2qimage(img_3)
    
    def get_current_pos(self):
        self.stage.get_absolute_postion()
        self.pos_list[self.next_count-1] = self.stage.absolute_position
        
    def finished(self):
        self.finished_signal.emit('finished')
        x_step = (self.pos_list[2][0] - self.pos_list[1][0]) / 2
        y_step = (self.pos_list[3][1] - self.pos_list[2][1]) / 2
        self.xy_step = np.array([int(x_step), int(y_step)])
        reply = QMessageBox.warning(self, "Warning", 'Do you want to save the new '+\
                                    'coordinates: x spacing '+ str(x_step)+'mm and y spacing '
                                    + str(y_step) + 'mm?', +\
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            np.savetxt(self.xy_step_file, self.xy_step)
        print(x_step, y_step)
        self.close()        
        
        
class CustomContrast(QWidget):
    confirmed = pyqtSignal(str)
    def __init__(self, default_name):
        super().__init__()
        self.default_name = default_name
        print(default_name)
        self.init_ui()
        
    def init_ui(self):
        label_name = QLabel(self)
        label_name.setText('Name: ')
        
        self.name_edit = QLineEdit(self)
        self.name_edit.setText(self.default_name)
        
        self.con_but_click_num = 0
        
        confirm_button = QPushButton('Confirm', self)
        confirm_button.clicked.connect(self.confirm)
        for sequence in ("Enter", "Return",):
            shorcut = QShortcut(sequence, confirm_button)
            shorcut.activated.connect(confirm_button.animateClick)
        
        cancel_button = QPushButton('Cancel', self)
        cancel_button.clicked.connect(self.cancel)
        
         
        hbox1 = QHBoxLayout()
        hbox1.addWidget(label_name)
        hbox1.addWidget(self.name_edit)
        
        hbox2 = QHBoxLayout()
        hbox2.addWidget(cancel_button)
        hbox2.addWidget(confirm_button)
        
        vbox = QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)

        self.setLayout(vbox)
        self.setWindowTitle('Custom Contrast')
        
    def confirm(self):
        if self.con_but_click_num == 0:
            self.con_but_click_num += 1
            
            self.name = self.name_edit.text()
            print(self.name)
            self.confirmed.emit('confirmed')    
   
    def cancel(self):
        self.close()     




class DeleteCustomContrast(QWidget):
    confirmed = pyqtSignal(str)
    def __init__(self, custom_contrast_list):
        super().__init__()
        self.custom_contrast_list = custom_contrast_list
        self.init_ui()
        
    def init_ui(self):
        self.qListWidget = QListWidget()
        
        
        self.check_box_list = []
        vbox = QVBoxLayout()
        for item in self.custom_contrast_list:
           self.check_box_list.append(QCheckBox(item, self))
           self.check_box_list[-1].setChecked(True)
           self.check_box_list[-1].toggle()
           
           qItem = QListWidgetItem(self.qListWidget)
           self.qListWidget.setItemWidget(qItem, self.check_box_list[-1])
#           vbox.addWidget(self.check_box_list[-1])
        
        vbox.addWidget(self.qListWidget)
        self.con_but_click_num = 0
        
        confirm_button = QPushButton('Confirm', self)
        confirm_button.clicked.connect(self.confirm)
        for sequence in ("Enter", "Return",):
            shorcut = QShortcut(sequence, confirm_button)
            shorcut.activated.connect(confirm_button.animateClick)
        
        cancel_button = QPushButton('Cancel', self)
        cancel_button.clicked.connect(self.cancel)
        
        hbox = QHBoxLayout()
        hbox.addWidget(cancel_button)
        hbox.addWidget(confirm_button)
        
        vbox.addLayout(hbox)
        
        self.setLayout(vbox)
        self.setWindowTitle('Delete Contrast')
        
    def confirm(self):
        if self.con_but_click_num == 0:
            self.con_but_click_num += 1
            self.delte_list = []
            
            for i in range(len(self.custom_contrast_list)):
                if self.check_box_list[i].isChecked():
                    self.delte_list.append(self.custom_contrast_list[i])
            
            self.confirmed.emit('confirmed')
   
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
        label_mag.setText('Magnification')
        
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
            
        
    
    
    