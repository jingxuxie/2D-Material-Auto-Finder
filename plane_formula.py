# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 22:44:22 2020

@author: HP
"""

import numpy as np
import time


def Get_Plane_Para(p1, p2, p3):
    x1, y1, z1 = p1[0], p1[1], p1[2]
    x2, y2, z2 = p2[0], p2[1], p2[2]
    x3, y3, z3 = p3[0], p3[1], p3[2]
    
    A = (y2 - y1)*(z3 - z1) - (z2 - z1)*(y3 - y1)
    B = (x3 - x1)*(z2 - z1) - (x2 - x1)*(z3 - z1)
    C = (x2 - x1)*(y3 - y1) - (x3 - x1)*(y2 - y1)
    
    D = -(A*x1 + B*y1 + C*z1)
    
    return [A, B, C, D]

def Get_Z_Position(x, y, para):
    A = para[0]
    B = para[1]
    C = para[2]
    D = para[3]
    z = (-D -A*x - B*y)/C
    return z

if __name__ == '__main__':
    
    para = Get_Plane_Para(*[[0,0,5000], [0,5000,4950], [5000,5000,4948]])
    print(para)
    time_start = time.time()
    for i in range(1):
        z = Get_Z_Position(1000,1000,para)
    time_end = time.time()
    print(time_end - time_start)
    print(z)