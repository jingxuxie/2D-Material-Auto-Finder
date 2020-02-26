# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 16:13:52 2020

@author: HP
"""

from PyQt5.QtCore import QThread, pyqtSignal
import win32gui
import win32api
import win32con
import time
from pywinauto.controls.win32_controls import EditWrapper, ListBoxWrapper,\
    ButtonWrapper
import cv2
import numpy as np
from plane_formula import Get_Plane_Para, Get_Z_Position
from layer_search import layer_search
from layer_search_TMD import layer_search_TMD
import os.path
from auxiliary_func import background_divide, get_folder_from_file
import sys
from PyQt5.QtWidgets import QApplication
from shutil import copyfile

class StageThread(QThread):
    stagestop = pyqtSignal(str)
    def __init__(self, camera, pos = [0,0]):
        super().__init__()
        self.camera = camera
        self.pos = pos
        self.absolute_position = [0, 0]
        self.initUI()
        
        
    def initUI(self):
        self.error = False
        self.prior_terminal_initial()
        
        
    def prior_terminal_initial(self):
        window_name = 'PriorTerminal'
        self.hwnd = win32gui.FindWindow(None, window_name)
        
        if self.hwnd == 0:
            print('no prior terminal')
            self.error = True
            
        else:
            hwnd = self.hwnd
            hwndChildList = []
            win32gui.EnumChildWindows(hwnd, lambda hwnd, param: param.append(hwnd), hwndChildList)
    
            self.prior_edit_text_hwnd = hwndChildList[-1]
            self.prior_edit_text = EditWrapper(self.prior_edit_text_hwnd)
            
            self.prior_list_box_hwnd = hwndChildList[-2]
            self.prior_list_box = ListBoxWrapper(self.prior_list_box_hwnd)

            self.manubar_hwnd = hwndChildList[2]
        
    def prior_pause(self):
        for i in range(200):
            list_box_text = self.prior_list_box.item_texts()
            if list_box_text[-1] == 'R':
                if len(list_box_text) > 100:
                    win32gui.SendMessage(self.hwnd, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)
                    win32gui.SetForegroundWindow(self.hwnd)
                    left, top, right, bottom = win32gui.GetWindowRect(self.manubar_hwnd)
                    win32api.SetCursorPos([left + int((right - left)/5*3), top + int((bottom - top)/2)])
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP | win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                    time.sleep(0.05)
                break
            else:
                time.sleep(0.02)
        if i == 199:
            print('prior pause time out!')
        
    def run(self):
        if self.error:
            self.stop()
            time.sleep(1)
        else:
            self.prior_edit_text.set_text('GR ' + str(self.pos[0]) + ' ' + \
                                          str(self.pos[1]))
            win32api.SendMessage(self.prior_edit_text_hwnd, win32con.WM_CHAR, 13, 0)
            time.sleep(0.1)
            self.prior_pause()            
    
            self.stop()
        
    def get_absolute_postion(self):
        pass
    
    def stop(self):
        print('stage stop')
        self.stagestop.emit('stop')
        
        
        
        
        
        
class AutoFocusThread(QThread):
    focus_finish = pyqtSignal(str)
    def __init__(self, camera, Fine = False):
        super().__init__()
        self.camera = camera
        self.Fine = Fine
        self.initUI()
        
    def initUI(self):
        self.radiant_mean = []
        self.bx2_position = 0
        self.focus = 0
        self.error = False
        self.BX2_initial()
    
    def BX2_initial(self):
        window_name = 'BX2 '
        bx2_hwnd = win32gui.FindWindow(None, window_name)
        
        if bx2_hwnd == 0:
            print('no bx2')
            self.error = True
            
        else:
            #还原窗口
            win32gui.SendMessage(bx2_hwnd, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)
            time.sleep(0.2)
            
            hwnd = bx2_hwnd
            hwndChildList = []
            win32gui.EnumChildWindows(hwnd, lambda hwnd, param: param.append(hwnd), hwndChildList)
    
            for child_hwnd in hwndChildList:
                classname = win32gui.GetClassName(child_hwnd)
                name = win32gui.GetWindowText(child_hwnd)
                if name == 'Focus' and classname == '#32770':
                    self.focus_hwnd = child_hwnd
                if classname == 'SysTabControl32':
                    self.left, self.top, self.right, self.bottom \
                    = win32gui.GetWindowRect(child_hwnd)
                    
            window_name = 'Soft Key'
            self.soft_key_hwnd = win32gui.FindWindow(None, window_name)
            #如果没有弹窗
            if self.soft_key_hwnd == 0:
                #前置窗口
                win32gui.SetForegroundWindow(bx2_hwnd)
                time.sleep(0.2)
                #按softkey
                #win32api.SetCursorPos([self.left + 130,self.top + 10])
                win32api.SetCursorPos([self.left + int((self.right-self.left)/5*2),self.top + 10])
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP | win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                time.sleep(0.7)
                
                #按左下角的东西
                win32api.SetCursorPos([self.left + int((self.right-self.left)/15),self.top + \
                                       int((self.bottom-self.top)/2*0.96)])
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP | win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                time.sleep(0.7)
            #再找一次
            self.soft_key_hwnd = win32gui.FindWindow(None, window_name)
            #如果找到了
            if self.soft_key_hwnd != 0:
                hwnd = self.soft_key_hwnd
                soft_key_hwndChildList = []
                win32gui.EnumChildWindows(hwnd, lambda hwnd, param: param.append(hwnd), \
                                          soft_key_hwndChildList)

                soft_key_1_hwnd = soft_key_hwndChildList[0]
                soft_key_2_hwnd = soft_key_hwndChildList[1]
                soft_key_3_hwnd = soft_key_hwndChildList[2]
                soft_key_4_hwnd = soft_key_hwndChildList[3]
                soft_key_5_hwnd = soft_key_hwndChildList[4]
                self.soft_key_1_button = ButtonWrapper(soft_key_1_hwnd)
                self.soft_key_2_button = ButtonWrapper(soft_key_2_hwnd)
                self.soft_key_3_button = ButtonWrapper(soft_key_3_hwnd)
                self.soft_key_4_button = ButtonWrapper(soft_key_4_hwnd)
                self.soft_key_5_button = ButtonWrapper(soft_key_5_hwnd)
                #按5
                self.soft_key_5_button.click()
                
            hwnd = self.focus_hwnd
            hwndChildList = []
            win32gui.EnumChildWindows(hwnd, lambda hwnd, param: param.append(hwnd), hwndChildList)
            focus_button = ButtonWrapper(hwndChildList[0])
            check_state = focus_button.get_check_state()
            if check_state == 1:
                self.bx2_edit_hwnd = hwndChildList[8]
                self.bx2_edit = EditWrapper(self.bx2_edit_hwnd)
                
                self.bx2_position_hwnd = hwndChildList[6]
                self.bx2_position = float(win32gui.GetWindowText(self.bx2_position_hwnd))
                
                self.up_height_hwnd = hwndChildList[4]
                self.up_height_button = ButtonWrapper(self.up_height_hwnd)
                
                self.down_height_hwnd = hwndChildList[11]
                self.down_height_button = ButtonWrapper(self.down_height_hwnd)
            else:
                print('focus not checked')
                self.error  =True
         
                
    def run(self):
        if self.error:
            self.stop()
            time.sleep(1)
        self.gradiant_mean = []
        self.click_go_height_wait(100)
        self.cal_clearness()
        for i in range(10):
            self.down_coarse()
            self.cal_clearness()
        z = 10 - np.argmax(self.gradiant_mean)
        self.click_go_height_wait(z*20)
        
#        with open('focus.txt','a') as file:
#            file.write(str(self.gradiant_mean)+'\n')
#            print('file write finished')
#        file.close()
            
        self.gradiant_mean = []
        self.click_go_height_wait(20)
        self.cal_clearness()
        for i in range(4):
            self.down_fine()
            self.cal_clearness()
        z = 4 - np.argmax(self.gradiant_mean)
        self.click_go_height_wait(z*10)

        if self.Fine:
            self.gradiant_mean = []
            self.click_go_height_wait(5)
            self.cal_clearness()
            for i in range(5):
                self.down_super_fine()
                self.cal_clearness()
            z = 5 - np.argmax(self.gradiant_mean)
            self.click_go_height_wait(z*2)
            
        self.bx2_position = float(win32gui.GetWindowText(self.bx2_position_hwnd))
        
        self.stop()
        
    def cal_clearness(self):
        img = self.camera.last_frame
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(img,cv2.CV_64F)
        self.gradiant_mean.append(np.var(abs(laplacian)))
        
    def up_coarse(self):
        self.soft_key_1_button.click()
        time.sleep(0.7)
    
    def down_coarse(self):
        self.soft_key_2_button.click()
        time.sleep(0.7)
    
    def down_fine(self):
        self.soft_key_3_button.click()
        time.sleep(0.7)
    
    def down_super_fine(self):
        self.soft_key_4_button.click()
        time.sleep(0.7)
        
    def go_height(self, z):
        if self.error:
            print('focus not checked!')
        else:
            self.bx2_edit.set_text(str(round(abs(z),2)))
#            time.sleep(0.1)
    
#            for i in range(3):
#                position_0 = win32gui.GetWindowText(self.bx2_position_hwnd)
            if z > 0:
                self.up_height_button.click()
            else:
                self.down_height_button.click()
#            time.sleep(0.5)
#                position_1 = win32gui.GetWindowText(self.bx2_position_hwnd)
#                if position_1 != position_0:
#                    break
    def click_go_height_wait(self, h):
        self.soft_key_5_button.click()
        time.sleep(0.5)
        self.go_height(h)
        time.sleep(0.5)

    def stop(self):
        print('focus stop')
        self.focus_finish.emit('stop')

        
        
        
        
        
class Set_Stage_Focus(QThread):
    
    def __init__(self, camera):
        super().__init__()
        self.camera = camera
        self.plane_points = []
        self.initUI()
        self.stage_running = True
        self.autofocus_running = True
        
    def initUI(self):
        self.stage = StageThread(self.camera)
        self.stage.stagestop.connect(self.stage_stop)
        self.autofocus = AutoFocusThread(self.camera)
        self.autofocus.focus_finish.connect(self.autofocus_stop)
    
    
    def stage_stop(self, s):
        if s == 'stop':
            self.stage_running = False
            
    def autofocus_stop(self, s):
        if s == 'stop':
            self.autofocus_running = False
            
    
    def wait_stage(self):
        for i in range(200):
            if not self.stage_running:
                print('wait_stage_finished')
                break
            else:
                time.sleep(0.02)
        if i == 199:
            self.stage.terminate()
            self.stage_running = False
            print('stage move time out!!!')
        
    
    def wait_focus(self):
        for i in range(300):
            if not self.autofocus_running:
                print('wait_focus_finished')
                break
            else:
                time.sleep(0.1)
        if i == 99:
            self.autofocus.terminate()
            self.autofocus_running = False
            print('focus time out!!!')
        
    
        
        
        
class FindFocusPlane(Set_Stage_Focus):
    find_focus_plane_stop = pyqtSignal(str)
    def __init__(self, camera):
        super().__init__(camera)
        self.para = [0, 0, 1, 0]
        
    def run(self):
        self.plane_points = []
        
        start_point = [1700, 1700]
        self.stage.pos = start_point
        self.stage_running = True
        self.stage.start()
        self.wait_stage()
        
        focus_point_1 = [0, 0]
        self.autofocus_running = True
        self.autofocus.start()        
        self.wait_focus()
        self.plane_points.append([focus_point_1[0] + start_point[0],\
                                  focus_point_1[1] + start_point[1],\
                                  self.autofocus.bx2_position])
        
        focus_point_2 = [0, 5000]
        self.stage.pos = focus_point_2
        self.stage_running = True
        self.stage.start()
        self.wait_stage()
        self.autofocus_running = True
        self.autofocus.start()
        self.wait_focus()
        self.plane_points.append([focus_point_2[0] + start_point[0],\
                                  focus_point_2[1] + start_point[1],\
                                  self.autofocus.bx2_position])
        
        focus_point_3 = [5000, 0]
        self.stage.pos = focus_point_3
        self.stage_running = True
        self.stage.start()
        self.wait_stage()
        self.autofocus_running = True
        self.autofocus.start()
        self.wait_focus()
        self.plane_points.append([focus_point_3[0] + start_point[0],\
                                  focus_point_2[1] + start_point[1],\
                                  self.autofocus.bx2_position])
        
        self.para = Get_Plane_Para(*self.plane_points)
        height = Get_Z_Position(0, 0, self.para)
        self.stage.pos = [-start_point[0] - focus_point_3[0],\
                          -start_point[1] - focus_point_2[1]]
        self.autofocus.go_height(height - self.plane_points[2][2])
        self.stage_running = True
        self.stage.start()
        self.wait_stage()
        
        print(self.plane_points, self.para)
        self.stop()
    
    def stop(self):
        self.find_focus_plane_stop.emit('stop')
        
        
        
class Scan(Set_Stage_Focus):
    scan_stop = pyqtSignal(str)
    def __init__(self, camera, plane_para = [0,0,1,0], magnification = '5x'):
        super().__init__(camera)
        self.plane_para = plane_para
        self.magnification = magnification
        self.rotate_90 = False
        
        self.date = time.strftime("%m-%d-%Y")
        self.save_folder = 'C:/jingxu'
        self.save_count = 1
        
        self.index = '00_00-00_00'
        
        self.current_dir = os.path.abspath(__file__).replace('\\','/')
        self.current_dir = get_folder_from_file(self.current_dir)
        self.bk_filename = self.current_dir + 'support_file/background/crop_x5.png'
        self.get_background()
        
    def run(self):
        if self.magnification == '5x':
            step = 2240
            x_sample = 5
            y_sample = 5
        elif self.magnification == '20x':
            step = 600
            x_sample = 20
            y_sample = 20
            self.bk_filename = self.current_dir + 'support_file/background/crop_x20.png'
            self.get_background()
        delta_x = abs(Get_Z_Position(5000, 0, self.plane_para) - \
                      Get_Z_Position(0, 0, self.plane_para))
        delta_y = abs(Get_Z_Position(0, 5000, self.plane_para) - \
                      Get_Z_Position(0, 0, self.plane_para))
        if delta_x > delta_y:
            self.rotate_90 = True
        height = []
        height_accu = 0
        height.append(Get_Z_Position(0, 0, self.plane_para))
        delta_height = 0
        
        while os.path.isfile(self.save_folder+'/'+self.date+'-'+str(self.save_count)+\
                             '-'+'00_00-00_00'+'.jpg'):
            self.save_count += 1
        img_temp = np.zeros((512,512,3), dtype = np.uint8)
        cv2.imwrite(self.save_folder+'/'+self.date+'-'+str(self.save_count)+\
                             '-'+'00_00-00_00'+'.jpg', img_temp)
        
        self.get_index(x_sample, y_sample, 0, 0)
        self.capture_save()
        
        for i in range(y_sample+1):
            for j in range(x_sample):
                time_start = time.time()
                if self.rotate_90:
                    height.append(Get_Z_Position(i*step, (j+1)*step, self.plane_para))
                else:
                    height.append(Get_Z_Position((j+1)*step, i*step, self.plane_para))
                delta_height = height[-1] - height[-2]
                height_accu += delta_height
                
                if abs(height_accu) > 3:
                    self.focus(height_accu)
                    height_accu = 0
                    time.sleep(0.1)
                
                if self.rotate_90:
                    self.move([0, step])
                    self.get_index(x_sample, y_sample, i, j+1)
                else:
                    self.move([step, 0])
                    self.get_index(x_sample, y_sample, j+1, i)
                time.sleep(0.1)
                self.capture_save()
                
                time_end = time.time()
                print(time_end - time_start)
                print(i,j)
                print('123')
            if i == y_sample:
                break
            else:
#                print('456')
                if self.rotate_90:
                    height.append(Get_Z_Position((i+1)*step, 0, self.plane_para))
                else:
                    height.append(Get_Z_Position(0, (i+1)*step, self.plane_para))
                delta_height = height[-1] - height[-2]
                height_accu += delta_height
                
                if abs(height_accu) > 3:
                    self.focus(height_accu)
                    height_accu = 0
                    time.sleep(0.1)
                
                if self.rotate_90:
                    self.move([step, -(j+1)*step])
                    self.get_index(x_sample, y_sample, i+1, 0)
                else:
                    self.move([-(j+1)*step, step])
                    self.get_index(x_sample, y_sample, 0, i+1)
                time.sleep(0.1)
                self.capture_save()
        
        self.stop()    
        
    def move(self, pos = [0, 0]):
        self.stage_running = True
        self.stage.pos = pos
        self.stage.start()
        self.wait_stage()
    
    def focus(self, h = 0):
        self.autofocus.go_height(h)
        
    def capture_save(self):
        #time.sleep(0.05)
        img = self.camera.last_frame
        left_crop = int(img.shape[1]*0.17)
        right_crop = int(img.shape[1]*0.83)
        img = img[:, left_crop:right_crop]
        img = background_divide(img, self.background, self.background_norm)

#        while os.path.isfile(self.save_folder+'/'+self.date+'-'+str(self.save_count)+\
#                             '-'+'00_00-00_00'+'.jpg'):
#            self.save_count += 1
        cv2.imwrite(self.save_folder+'/'+self.date+'-'+str(self.save_count)+\
                    '-'+self.index+'.jpg', img)
#        self.save_count += 1
    
    
    def get_index(self, total_x, total_y, x, y):
        size_x = self.int2str(total_x)
        size_y = self.int2str(total_y)
        pos_x = self.int2str(x)
        pos_y = self.int2str(y)
        
        self.index = size_x+'_'+size_y+'-'+pos_x+'_'+pos_y
        
    def int2str(self, num):
        if num > 9:
            return str(num)
        else:
            return '0'+str(num)
    
    def get_background(self):
        self.background = cv2.imread(self.bk_filename)
        self.background_norm = np.zeros(3)
        for i in range(3):
            self.background_norm[i] = np.mean(self.background[:,:,i])
            print(self.background_norm[i])
    
    def stop(self):
        self.scan_stop.emit('stop')
        
        


class LayerSearchThread(QThread):
    def __init__(self, thickness = '285nm', material = 'graphene'):
        super().__init__()
        self.thickness = thickness
        self.material = material
        self.filepath = 'C:/jingxu'
        self.pathDir =  os.listdir(self.filepath)
#        self.pathDir.sort(key= lambda x:int(x[11:-16]))#按数字排序
        
        self.outpath = 'C:/temp'
        self.finishedDir = os.listdir(self.outpath)
        self.finished_count = len(self.finishedDir)
        
        self.resultpath = 'C:/results'
    
    def run(self):
        #i = 0
        while True:
            
            self.pathDir =  os.listdir(self.filepath)
#            self.pathDir.sort(key= lambda x:int(x[11:-16]))#按数字排序
            time.sleep(1)
#            time_start = time.time()
#            record_len = len(self.pathDir)
            for self.finished_count in range(len(self.pathDir)):
                output_name = self.outpath+'/'+self.pathDir[self.finished_count]
                if not os.path.isfile(output_name):
                    input_name = self.filepath+'/'+self.pathDir[self.finished_count]
    #                print(input_name)
                    output_name = self.outpath+'/'+self.pathDir[self.finished_count]
                    result_name = self.resultpath+'/'+self.pathDir[self.finished_count]
                    if self.material == 'graphene':
                        ret, img_out = layer_search(input_name, self.thickness)
                    elif self.material == 'TMD':
                        ret, img_out = layer_search_TMD(input_name, self.thickness)
                    else:
                        print('layer setting error')
#                    img_out = self.draw_postition(self.pathDir[self.finished_count], img_out)
                    cv2.imwrite(output_name, img_out)
                    if ret:
                        copyfile(output_name, result_name)
                
#                self.finished_count += 1
                
                
    def draw_postition(self, filename, img_out):
        index = filename[-15:-4]
        size_x = int(index[:2])
        size_y = int(index[3:5])
        pos_x = int(index[6:8])
        pos_y = int(index[9:11])
        
        if size_x == 0 or size_y == 0:
            return img_out
        
        rec_x1 = img_out.shape[1] - 300
        rec_y1 = 100
        rec_x2 = rec_x1 + 200
        rec_y2 = rec_y1 + 200
        
        #print(rec_x1, rec_y1)
        px = rec_x2 - int((rec_x2 - rec_x1)/size_x*pos_x)
        py = rec_y2 - int((rec_y2 - rec_y1)/size_y*pos_y)
        
        
        img_out = cv2.rectangle(img_out,(rec_x1,rec_y1),(rec_x2,rec_y2),(0,255,0),3)
        img_out = cv2.circle(img_out,(px,py), 10, (0,0,255), -1)
        
        return img_out
            
    
    def stop(self):
        pass
    
    
    
class LargeScanThread(QThread):
    large_scan_stop = pyqtSignal(str)
    def __init__(self, camera, thickness = '285nm', magnification = '5x', \
                 material = 'graphene'):
        super().__init__()
        self.camera = camera
        self.para = [0, 0, 1, 0]
        self.find_focus_plane_running = True
        self.scan_running = True
        self.thickness = thickness
        self.magnification = magnification
        self.material = material
        self.init_ui()
    
    def init_ui(self):
        self.stage_focus = Set_Stage_Focus(self.camera)
        self.find_focus_plane = FindFocusPlane(self.camera)
        self.find_focus_plane.find_focus_plane_stop.connect(self.stop_find_focus_plane)
        self.scan = Scan(self.camera)
        self.scan.scan_stop.connect(self.stop_scan)
        self.layer_search = LayerSearchThread()
        
        
    def run(self):
        self.scan.magnification = self.magnification
        self.layer_search.thickness = self.thickness
        self.layer_search.material = self.material
        self.layer_search.start()
        if self.magnification == '20x':
            self.find_focus_plane.autofocus.Fine = True
        for m in range(3):
            for n in range(2):
                self.find_focus_plane.start()
                self.find_focus_plane_running = True
                self.wait_for_find_focus_plane()
                
                self.para = self.find_focus_plane.para
                self.scan.plane_para = self.para
                self.scan_running = True
                self.scan.start()
                self.wait_for_scan()
                
                self.stage_focus.stage.pos = [3800,-11200]
                self.stage_focus.stage_running = True
                self.stage_focus.stage.start()
                self.stage_focus.wait_stage()
                
            self.find_focus_plane.start()
            self.find_focus_plane_running = True
            self.wait_for_find_focus_plane()
            
            self.para = self.find_focus_plane.para
            self.scan.plane_para = self.para
            self.scan_running = True
            self.scan.start()
            self.wait_for_scan()
            if m == 2:
                break
            else:
                self.stage_focus.stage.pos = [-41200,3800]
                self.stage_focus.stage_running  =True
                self.stage_focus.stage.start()
                self.stage_focus.wait_stage()


    def stop_find_focus_plane(self, s):
        if s == 'stop':
            #self.stage.terminate()
            self.find_focus_plane_running = False
            
    def stop_scan(self, s):
        if s == 'stop':
            self.scan_running = False
        
    def wait_for_find_focus_plane(self):
        for i in range(2000):
            if not self.find_focus_plane_running:
                print('wait find focus plane finished')
                break
            else:
                time.sleep(0.1)
        if i == 199:
            self.find_focus_plane.terminate()
            self.find_focus_plane_running = False
            print('wait find focus plane time out')
    
    def wait_for_scan(self):
        for i in range(10000):
            if not self.scan_running:
                print('wait scanning finished')
                break
            else:
                time.sleep(0.1)
        if i == 999:
            self.scan.terminate()
            self.scan_running = False
            print('wait scan time out')
            
        
        
            



          
if __name__=='__main__':
    app = QApplication(sys.argv)
    a = LayerSearchThread()
    a.start()
    b = a.pathDir
    sys.exit(app.exec_())

        
    
            
    
    
        
        
        
    
