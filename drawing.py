# -*- coding: utf-8 -*-
"""
Created on Sat Jan 25 20:27:44 2020

@author: HP
"""

import numpy as np
import cv2


class Shape:
    def get_pos(self):
        return self.pos

    def get_width(self):
        return self.width
    
    def get_color(self):
        return self.color


class Line():
    def __init__(self, x1 = 0, y1 = 0, x2 = 0, y2 = 0, canvas_width = 1, canvas_height = 1,\
                 color = (255, 0, 0), width = 1, num = 0, show_distance = False):
        self.x1 = x1
        self.y1 = y1
        
        self.x2 = x2
        self.y2 = y2
        
        self.x1_show, self.y1_show = self.x1, self.y1
        self.x2_show, self.y2_show = self.x2, self.y2
        
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        
        self.pos_refresh()
        
        self.width = width
        self.color = color
        self.num = num
        self.show_distance = show_distance
        
        #用来标记是哪种形状
        self.prop = 'line'
        
        
    def pos_refresh(self):
        self.pos1 = (self.x1_show, self.y1_show)
        self.pos2 = (self.x2_show, self.y2_show)
        self.pos = [self.pos1, self.pos2]
        
        
class Rectangle():
    def __init__(self, x1 = 0, y1 = 0, x2 = 0, y2 = 0 , canvas_width = 1, canvas_height = 1, \
                 color = (255, 0, 0), width = 1, num = 0, show_side_length = False):
        self.x1 = min(x1, x2)
        self.x2 = max(x1, x2)
        
        self.y1 = min(y1, y2)
        self.y2 = max(y1, y2)
        
        self.x1_show, self.y1_show = self.x1, self.y1
        self.x2_show, self.y2_show = self.x2, self.y2
        
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

        self.pos_refresh()
        
        self.width = width
        self.color = color
        self.num = num
        self.show_side_length = show_side_length
        
        self.prop = 'rec'
        
    def pos_refresh(self):
        self.pos1 = (self.x1_show, self.y1_show)
        self.pos2 = (self.x2_show, self.y2_show)
        self.pos = [self.pos1, self.pos2]
        
        
        
class Circle():
    def __init__(self, x1 = 0, y1 = 0, x2 = 0, y2 = 0, canvas_width = 1, canvas_height = 1, \
                 color = (255, 0, 0), width = 1, num = 0, show_radius = False):
        self.x1 = x1
        self.y1 = y1
        
        self.x2 = x2
        self.y2 = y2
        
        self.x1_show, self.y1_show = self.x1, self.y1
        self.x2_show, self.y2_show = self.x2, self.y2
        
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        
        self.pos_refresh()

        self.width = width
        self.color = color
        self.num = num
        self.show_radius = show_radius   
        
        self.prop = 'circle'
    
    def pos_refresh(self):
        self.center_x = int(round((self.x1 + self.x2)/2))
        self.center_y = int(round((self.y1 + self.y2)/2))
        
        radius = np.sqrt((self.x2 - self.x1)**2 + (self.y2 - self.y1)**2)
        self.radius = int(round(radius/2))
        
        self.center_x_show = round((self.x1_show + self.x2_show)/2)
        self.center_y_show = round((self.y1_show + self.y2_show)/2)
        self.pos = [(self.center_x_show, self.center_y_show)]
        
        radius_show = np.sqrt((self.x2_show - self.x1_show)**2 + (self.y2_show - self.y1_show)**2)
        self.radius_show = int(round(radius_show/2))


class Eraser():
    def __init__(self, x1 = 0, y1 = 0, size = 13, color = (220,220,220,200), width = -1, num = [0]):
        self.x1 = x1
        self.y1 = y1
        
        self.x1_show = x1
        self.y1_show = y1
        
        self.pos_refresh()
        
        self.size = size
        self.color = color
        self.num = num
        self.width = width
        
        self.prop = 'eraser'
        
    def pos_refresh(self):
        self.pos = [(self.x1_show, self.y1_show)]
        
        
class Point():
    def __init__(self, x1 = 0, y1 = 0):
        self.x1 = x1
        self.y1 = y1
        
        self.x1_show = x1
        self.y1_show = y1
        
        self.pos_refresh()
        
        self.prop = 'point'
        
    def pos_refresh(self):
        self.pos = [(self.x1_show, self.y1_show)]


        
class Clear_All():
    def __init__(self):
        self.prop = 'clear'
        
        
if __name__ == '__main__':

    img = np.zeros((512,512,3), np.uint8)
    shape = []
    shape.append(Line(1,2,3,4,[0,255,0],3))
    shape.append(Line(3,4,5,6))
    shape.append(Rectangle(6,9,11,-1))
    shape.append(Circle(10,10,10, width = 1))
    shape.append(Eraser(200,200, size = 10))
    shape.append(Clear_All())
    
#    print(shape[0].get_pos())
#    print(shape[1].get_pos())       
    print(shape[2].pos1) 
    #print(shape[3].center)
    cv2.circle(img,*shape[4].pos, shape[4].size,shape[4].color, shape[4].width)
    cv2.imshow('1',img)