# -*- coding: utf-8 -*-
"""
Created on Sat Nov 23 10:35:36 2019

@author: Jingxu Xie (Best Sir Zhang)
"""

import numpy as np
import cv2
from PyQt5.QtCore import Qt
import os

class Camera:
    def __init__(self, cam_num):
        self.cam_num = cam_num
        self.cap = None
        self.current_dir = os.path.abspath(__file__).replace('\\','/')
        self.current_dir = self.get_folder_from_file(self.current_dir)
        self.current_dir = self.current_dir+'support_file/'
        self.initial_img_error = False
        self.initial_last_frame()
        self.camera_error = False

    def initial_last_frame(self):
        self.last_frame = cv2.imread(self.current_dir+'no_camera.png')
        if self.last_frame is None:
            self.initial_img_error = True
            self.last_frame = np.zeros((512,512,3), np.uint8)

    def initialize(self):
        self.cap = cv2.VideoCapture(self.cam_num)
        #print(self.cam_num)

    
    def get_frame(self):
        self.ret = False
        try:
            self.ret, self.last_frame_temp = self.cap.read()
            #print(self.ret)
            #print('456')
        except:
            #print('789')
            self.camera_error = True
            self.initial_last_frame()
        else:
            if self.ret == True:
                #self.last_frame_temp = cv2.resize(self.last_frame_temp,(1536,864))
                #这个写进主函数中，release时取所有4k大像素
                #self.last_frame_temp = cv2.cvtColor(self.last_frame_temp,cv2.COLOR_BGR2RGB)
                self.last_frame = self.last_frame_temp
            else:
                #print('error')
                self.initial_last_frame()
        if self.ret != True:
            self.camera_error = True
        return self.last_frame

    def acquire_movie(self):
        while True:
            self.get_frame()
            #movie.append(self.get_frame())
        #return movie
        
    def set_brightness(self, value):
        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, value)
        
    def get_brightness(self):
        return self.cap.get(cv2.CAP_PROP_BRIGHTNESS)

    def __str__(self):
        return 'OpenCV Camera {}'.format(self.cam_num)
    
    def close_camera(self):
        self.cap.release()
    
    def get_folder_from_file(self, filename):
        folder = filename
        while folder[-1] != '/':
            folder = folder[:-1]
        return folder

if __name__ == '__main__':
    cam = Camera(0)
    cam.initialize()
    print(cam)
    frame = cam.get_frame()
    cv2.imshow('1',frame)
    #cam.close_camera()
    #del cam

    cam = Camera(0)
    cam.initialize()
    print(cam)
        
    frame0 = cam.get_frame()
    cv2.imshow('1',frame0)
    cv2.waitKey(1000)
    #print(frame)
    '''
    cam.set_brightness(1)
    print(cam.get_brightness())
    cam.set_brightness(1.9)
    print(cam.get_brightness())
    '''
    cam.close_camera()
    