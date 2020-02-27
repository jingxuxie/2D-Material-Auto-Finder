# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 10:50:53 2020

@author: HP
"""

import cv2
import numpy as np
from matplotlib import pyplot as plt
import sys
import scipy.signal as signal 
import time
from numba import jit
from shutil import copyfile
import os

time_start = time.time()



def find_min_not_zero(data):
    for i in range(len(data)):
        if data[i]>0:
            return i
    return i



def find_real_peak_pos(img0):
    img = img0.copy()
    
    increase_contr_factor = 255/np.max(img) - 0.001
    img_increase_contr = (img*increase_contr_factor).astype(np.uint8)

    hist_increase_contr = cv2.calcHist([img_increase_contr], [0], None, [255], [1,255])
#    plt.plot(hist_increase_contr)
    
    pos1 = signal.argrelextrema(hist_increase_contr, np.greater)
    peak1 = hist_increase_contr[pos1]
    average_value = np.mean(peak1)
    
    if len(pos1[0]) > 0:
        pos_temp = signal.argrelextrema(peak1, np.greater)
        pos2 = pos1[0][pos_temp].tolist()
        peak2 = peak1[pos_temp].tolist()
    else:
        return [0], img_increase_contr
    
    if len(pos2) > 0:
        i = 0
        while i < len(peak2):
            if peak2[i] < average_value:
                peak2.pop(i)
                pos2.pop(i)
                i -= 1
            i += 1
#            plt.scatter(pos2, peak2, marker = '*', linewidth = 10)
            if i == len(peak2):
                break
            
    if not len(pos2) > 0:
        peak_max = pos1[0][np.argmax(peak1)]
        return [int(peak_max)], img_increase_contr
    
#    plt.plot(pos1[0], peak1)

    return pos2, img_increase_contr
    
    
#疑似应该+1
def find_peak_boundary(pos):
    if pos[0] == 0:
        return [0,0]
    else:
        boundary_start = max(0, pos[0] - 5.5)
        boundary_end = min(255, pos[-1] + 5.5)
        boundary = [boundary_start]
        i = 0
        while i < (len(pos) - 1):
            d = pos[i + 1] - pos[i]
            if d >= 10:
                boundary.append(pos[i] + 5.5)
                boundary.append(pos[i + 1] - 5.5)
            elif 5 <= d <10:
                boundary.append(pos[i] + d/2)
                boundary.append(pos[i + 1] - d/2)
            elif d < 5:
                pass
            i += 1
        boundary.append(boundary_end)
    return boundary
             
   



def find_contours(img0, cnt_large, boundary, img_raw, bk_color):
    if boundary[0] == 0 and boundary[1] == 0:
        return [], []
    
    img = img0.copy()
    #factor = 255/np.max(img) - 0.001
    #img = (img*factor).astype(np.uint8)
    
    mask = np.zeros(img.shape, dtype = np.uint8)
    contour_segmentation = []
    contrast_segmentation = []
    for i in range(int(len(boundary)/2)):
        lowerBound, upperBound = boundary[2*i], boundary[2*i + 1]
        cv2.inRange(img, lowerBound, upperBound, mask)
        
        kernel = np.ones((3,3),np.uint8)
        opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        kernel = np.ones((3,3),np.uint8)
        closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
        
        out, contours_small, hierarchy = \
        cv2.findContours(closing,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
        
        area = 0
        if len(contours_small) > 0:
            i = 0
            while i < len(contours_small):
                area_temp = cv2.contourArea(contours_small[i])
                #print(area_temp)
                if area_temp < 100 or not is_wanted(img_raw, contours_small[i], bk_color):
                    contours_small.pop(i)
                    i -=  1
                else:
                    area += area_temp
                i += 1
            #print(area)
            if area > 100:
                contour_segmentation.append(contours_small)
                #print('yes!')
                pass
    #print(len(contour_segmentation))
    
    if len(contour_segmentation) > 0:
        #print(len(contour_segmentation))
        mask = np.zeros(img.shape, np.uint8)
        i = 0
        while i < len(contour_segmentation):
            mask_temp = np.zeros(img.shape,np.uint8)
            cv2.drawContours(mask_temp,contour_segmentation[i],-1,255,-1)
            
            #这两行用于抠出所有segments
            cv2.drawContours(mask,contour_segmentation[i],-1,255,-1)
            img_segment = cv2.bitwise_and(img, img, mask = mask)
            cv2.drawContours(img_segment,contour_segmentation[i],-1,255,-1)
        
            mean_val = cv2.mean(img_raw,mask = mask_temp)
            mean_val_y = mean_val[2]*0.299 + mean_val[1]*0.587 + mean_val[0]*0.114
            contrast_g = (bk_color[2] - mean_val[1]) / bk_color[2]
            contrast_r = (bk_color[3] - mean_val[2]) / bk_color[3]
            diff = max(0.03, contrast_g*0.2)
#            if abs(contrast_r - contrast_g) > diff:
#                contour_segmentation.pop(i)
#                i -= 1
#            else:
#            print('contrast', contrast)
#            if contrast > 0.3 or contrast < 0.025:
#                contour_segmentation.pop(i)
#                i -= 1
#            else:
            local_contrast = calculate_local_contrast(img_raw, cnt_large, \
                                                      mean_val_y, bk_color[0])
            if local_contrast > 0.3 or local_contrast < 0.028:
                contour_segmentation.pop(i)
                i -= 1
            else:
                contrast_segmentation.append(local_contrast)
            i += 1
            #print(mean_val)
            #print((bk_color_g - mean_val[1]) / bk_color_g)
            
#        cv2.imshow('mask',img_segment)
            
    return contour_segmentation, contrast_segmentation


def calculate_local_contrast(img_raw, cnt_large, sample_value, bk_color_y):
    #use gray scale
    local_bk = sample_value
    
    x,y,w,h = cv2.boundingRect(cnt_large)
    enlarge_rate = 0.13
    start_1 = max(0, y-int(h*enlarge_rate))
    end_1 = min(img_raw.shape[0]-1, y+int(h*(1+enlarge_rate*2)))
    start_2 = max(0, x-int(w*enlarge_rate))
    end_2 = min(img_raw.shape[1]-1, x+int(w*(1+enlarge_rate*2)))
    img_rec = img_raw[start_1: end_1, start_2: end_2, :]
    
    img_rec = cv2.cvtColor(img_rec, cv2.COLOR_BGR2GRAY)
    
    hist = cv2.calcHist([img_rec], [0], None, [256], [0,255])
    hist_max = np.max(hist)
    hist_cut_start = int(round(sample_value + 1))
    hist_cut_end = int(round(bk_color_y + 5.5))
    hist_cut = hist[hist_cut_start: hist_cut_end]
    
    pos = signal.argrelextrema(hist_cut, np.greater)[0]
    peaks = hist_cut[pos]
    peak_temp = 0
    pos_temp = 0
    for i in range(len(peaks)):
        if peaks[i] >= hist_max/3:
            if peaks[i] > peak_temp:
                peak_temp = peaks[i]
                pos_temp = pos[i]
    if pos_temp != 0:
        local_bk = pos_temp + hist_cut_start 
    
    local_contrast = (local_bk - sample_value)/local_bk
#    print(local_contrast)
    return local_contrast


def is_wanted(img_raw, contour, bk_color):
    area = cv2.contourArea(contour)
    mask = np.zeros((img_raw.shape[0], img_raw.shape[1]), dtype = np.uint8)
    cv2.drawContours(mask, [contour],-1,255,-1)
    segment = cv2.bitwise_and(img_raw, img_raw, mask = mask)
    
    b,g,r = cv2.split(segment)
    hist_b = cv2.calcHist([b], [0], None, [256], [1,255])
    hist_g = cv2.calcHist([g], [0], None, [256], [1,255])
    hist_r = cv2.calcHist([r], [0], None, [256], [1,255])
#    plt.plot(hist_b,color = 'b')
#    plt.plot(hist_g,color = 'g')
#    plt.plot(hist_r,color = 'r')
    b_max_pos = np.argmax(hist_b)
    g_max_pos = np.argmax(hist_g)
    r_max_pos = np.argmax(hist_r)
    
    if bk_color[3] - bk_color[2] > 10:
        if r_max_pos < g_max_pos:
            return False
    
    if r_max_pos < 50:
        return False
#        r_max = np.max int('123')
    return True
            
    
    
    


def layer_search(filename, thickness = '285nm'):
    img0 = cv2.imread(filename)
    img_raw = img0.copy()
    img_raw_draw = img0.copy()
    img = img0
    isLayer = False
    #img_raw = cv2.pyrDown(img)
    
    #bk_color = fv(img)
    
    b,g,r = cv2.split(img)
    hist_b = cv2.calcHist([b], [0], None, [256], [0,255])
    hist_g = cv2.calcHist([g], [0], None, [256], [0,255])
    hist_r = cv2.calcHist([r], [0], None, [256], [0,255])
    
    img = cv2.cvtColor(img_raw, cv2.COLOR_BGR2GRAY)
    hist_y = cv2.calcHist([img], [0], None, [256], [0,255])
    
    #img = cv2.medianBlur(img,3)
    #img = cv2.GaussianBlur(img, (3,3), sigmaX = 1.5, sigmaY = 1.5)
    #img = cv2.fastNlMeansDenoising(img, None, 5, 3, 11)
    
#    plt.plot(hist_y)
    bk_color_y = np.argmax(hist_y)
    bk_color_b = np.argmax(hist_b)
    bk_color_g = np.argmax(hist_g)
    bk_color_r = np.argmax(hist_r)
    bk_color = [bk_color_y, bk_color_b, bk_color_g, bk_color_r]
    #laplacian = cv2.Laplacian(img,cv2.CV_64F)
    
    #edges = cv2.Canny(img,0,20)
    
    threshold = bk_color_y - 5
    
    ret,img_binary = cv2.threshold(img,threshold,255,cv2.THRESH_BINARY_INV)
    
    kernel_open = np.ones((5,5),np.uint8)
    img_open = cv2.morphologyEx(img_binary, cv2.MORPH_OPEN, kernel_open)
    
    kernel_close = np.ones((5,5),np.uint8)
#    img_close = cv2.morphologyEx(img_open, cv2.MORPH_CLOSE, kernel_close)
    img_close = img_open
    _, contours, hierarchy_ = \
    cv2.findContours(img_close,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    
    
    
    cnt_large_ensemble = []
    for i in range(len(contours)):
        area = cv2.contourArea(contours[i])
        #print(area)
        if area >300:
            cnt_large_ensemble.append(contours[i])
        
    #画出所有轮廓    
    image = cv2.drawContours(img0, cnt_large_ensemble, -1, (0,0,255), 3)
#    cv2.imshow('3', image)


    for cnt_large in cnt_large_ensemble[:]:
        mask = np.zeros(img.shape,np.uint8)
        cv2.drawContours(mask,[cnt_large],-1,255,-1)
        
        #pixelpoints = np.transpose(np.nonzero(mask))
        
        #edges = cv2.Canny(img,0,20, mask = mask)
        
        #mean_val = cv2.mean(image,mask = mask)
        #print((threshold - mean_val[1]) / threshold)
       
        img_cnt_large_cut = cv2.bitwise_and(img_raw, img_raw, mask = mask)
#        cv2.imshow('img', img_cnt_large_cut)
        hist_b_temp = cv2.calcHist([img_cnt_large_cut], [0], None, [255], [1,255])
        hist_g_temp = cv2.calcHist([img_cnt_large_cut], [1], None, [255], [1,255])
        hist_r_temp = cv2.calcHist([img_cnt_large_cut], [2], None, [255], [1,255])

        #去除大轮廓的峰的蓝色小于100的， 针对285有效，即去除黑的部分
#        if hist_temp[30] > 0:
        
        if thickness == '285nm':
            if np.argmax(hist_b_temp) < 100 or hist_g_temp[30] > 10:
                continue
        elif thickness == '90nm':
            if np.argmax(hist_b_temp) < 50:
                continue
            
#        plt.plot(hist_b_temp,color = 'b')
#        plt.plot(hist_g_temp,color = 'g')
#        plt.plot(hist_r_temp,color = 'r')
        img_cnt_large_cut = cv2.cvtColor(img_cnt_large_cut, cv2.COLOR_BGR2GRAY)
#        cv2.imshow('img', img_cnt_large_cut)
        
        hist_peak_pos, img_cnt_large_incr_contr = find_real_peak_pos(img_cnt_large_cut)
        hist_peak_bd = find_peak_boundary(hist_peak_pos)
        cnt_small_ensemble, contrast = find_contours(img_cnt_large_incr_contr, cnt_large,\
                                                     hist_peak_bd, img_raw, bk_color)
        k = 0
        for cnt_smalls in cnt_small_ensemble[:]:
            area_temp = 0
            index_max_area = 0
            for i in range(len(cnt_smalls)):
                if cv2.contourArea(cnt_smalls[i]) > area_temp:
                    area_temp = cv2.contourArea(cnt_smalls[i])
                    index_max_area = i
            
            mask = np.zeros(img.shape, dtype = np.uint8)
            cv2.drawContours(mask, cnt_smalls, -1, 255, -1)
            
            img_samll_segment = cv2.bitwise_and(img_raw, img_raw, mask = mask)
            
            x,y,w,h = cv2.boundingRect(cnt_large)
            enlarge_rate = 0.2
            start_1 = max(0, y-int(h*enlarge_rate))
            end_1 = min(img_raw.shape[0]-1, y+int(h*(1+enlarge_rate*2)))
            start_2 = max(0, x-int(w*enlarge_rate))
            end_2 = min(img_raw.shape[1]-1, x+int(w*(1+enlarge_rate*2)))
#            cv2.rectangle(img_raw_draw,(x,y),(x+w,y+h),(0,255,0),2)
            cv2.rectangle(img_raw_draw,(start_2,start_1),(end_2,end_1),(0,255,0),2)
            
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(img_raw_draw,str(round(contrast[k],3)),(int(x),int(y+h)), font, 1,(255,255,255),2,cv2.LINE_AA)
            isLayer = True
            k += 1
    
#    cv2.imshow('1', img_binary)
#    cv2.imshow('2-1', img_open)
#    cv2.imshow('2-2', img_close)
#    cv2.imshow('4', img_raw_draw)
    return isLayer, img_raw_draw
    
#    cv2.imwrite(outname, img_raw)
#    if isLayer:
#        copyfile(outname, copyname)

def test_run(thickness = '285nm'):
    print(thickness)
    filepath = 'C:/jingxu'
    pathDir =  os.listdir(filepath)
    outpath = 'C:/temp'
    resultpath = 'C:/results'
    finished_count = 0
    for finished_count in range(len(pathDir)):
        output_name = outpath+'/'+pathDir[finished_count]
        input_name = filepath+'/'+pathDir[finished_count]
#                print(input_name)
        output_name = outpath+'/'+pathDir[finished_count]
        result_name = resultpath+'/'+pathDir[finished_count]
        ret, img_out = layer_search(input_name, thickness)
        cv2.imwrite(output_name, img_out)
        if ret:
            copyfile(output_name, result_name)

if __name__ == '__main__':
#    img0 = cv2.imread('F:/2019/12/20/norm_bk/topleft/12-20-2019-50.jpg')
#    img0 = cv2.imread('F:/2020/1/25/01-28-2020-36.jpg')
    layer_search('F:/2020/1/21/01-21-2020-102.jpg', thickness='90nm')
#    test_run('90nm')
    
    #img0 = cv2.resize(img0, (1200,800))
    '''
    img_raw = img0.copy()
    img = img0
    #img_raw = cv2.pyrDown(img)
    
    #bk_color = fv(img)
    
    b,g,r = cv2.split(img)
    hist_b = cv2.calcHist([b], [0], None, [256], [0,255])
    hist_g = cv2.calcHist([g], [0], None, [256], [0,255])
    hist_r = cv2.calcHist([r], [0], None, [256], [0,255])
    
    img = cv2.cvtColor(img_raw, cv2.COLOR_BGR2GRAY)
    hist_y = cv2.calcHist([img], [0], None, [256], [0,255])
    
    #img = cv2.medianBlur(img,3)
    #img = cv2.GaussianBlur(img, (3,3), sigmaX = 1.5, sigmaY = 1.5)
    #img = cv2.fastNlMeansDenoising(img, None, 5, 3, 11)
    
    #plt.plot(hist_y)
    bk_color_y = np.argmax(hist_y)
    bk_color_b = np.argmax(hist_b)
    bk_color_g = np.argmax(hist_g)
    bk_color_r = np.argmax(hist_r)
    #laplacian = cv2.Laplacian(img,cv2.CV_64F)
    
    #edges = cv2.Canny(img,0,20)
    
    threshold = bk_color_y - 5
    
    ret,img_binary = cv2.threshold(img,threshold,255,cv2.THRESH_BINARY_INV)
    
    kernel_open = np.ones((5,5),np.uint8)
    img_open = cv2.morphologyEx(img_binary, cv2.MORPH_OPEN, kernel_open)
    
    kernel_close = np.ones((7,7),np.uint8)
    img_close = cv2.morphologyEx(img_open, cv2.MORPH_CLOSE, kernel_close)
    
    _, contours, hierarchy_ = \
    cv2.findContours(img_close,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    
    cnt_large_ensemble = []
    for i in range(len(contours)):
        area = cv2.contourArea(contours[i])
        #print(area)
        if area >1000:
            cnt_large_ensemble.append(contours[i])
        
    #画出所有轮廓    
    image = cv2.drawContours(img0, cnt_large_ensemble, -1, (0,0,255), 3)


    for cnt_large in cnt_large_ensemble[:] :
        mask = np.zeros(img.shape,np.uint8)
        cv2.drawContours(mask,[cnt_large],-1,255,-1)
        
        #pixelpoints = np.transpose(np.nonzero(mask))
        
        #edges = cv2.Canny(img,0,20, mask = mask)
        
        #mean_val = cv2.mean(image,mask = mask)
        #print((threshold - mean_val[1]) / threshold)
       
        img_cnt_large_cut = cv2.bitwise_and(img_raw, img_raw, mask = mask)
        img_cnt_large_cut = cv2.cvtColor(img_cnt_large_cut, cv2.COLOR_BGR2GRAY)
        
        hist_peak_pos, img_cnt_large_incr_contr = find_real_peak_pos(img_cnt_large_cut)
        hist_peak_bd = find_peak_boundary(hist_peak_pos)
        cnt_small_ensemble, contrast = find_contours(img_cnt_large_incr_contr, hist_peak_bd)
        
        k = 0
        for cnt_smalls in cnt_small_ensemble[:]:
            area_temp = 0
            index_max_area = 0
            for i in range(len(cnt_smalls)):
                if cv2.contourArea(cnt_smalls[i]) > area_temp:
                    area_temp = cv2.contourArea(cnt_smalls[i])
                    index_max_area = i
            
            mask = np.zeros(img.shape, dtype = np.uint8)
            cv2.drawContours(mask, cnt_smalls, -1, 255, -1)
            
            img_samll_segment = cv2.bitwise_and(img_raw, img_raw, mask = mask)
            
            x,y,w,h = cv2.boundingRect(cnt_smalls[index_max_area])
            cv2.rectangle(img_raw,(x,y),(x+w,y+h),(0,255,0),2)
            
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(img_raw,str(round(contrast[k],3)),(int(x),int(y+h)), font, 1,(255,255,255),2,cv2.LINE_AA)
            
            k += 1
    cv2.imshow('test', img_raw)
          '''

#hist = cv2.calcHist([img1_bg], [0], None, [255], [1,255])
#'''
#min_value = find_min_not_zero(hist)
#img1_bg = img1_bg.astype(int) - min_value + 5
#img1_bg = np.maximum(0, img1_bg)
#'''
##factor = 255/np.max(img1_bg) - 0.001
##img1_bg = (img1_bg*factor).astype(np.uint8)
#hist = cv2.calcHist([img1_bg], [0], None, [255], [1,255])
#cv2.imshow('test',img1_bg)
##r,g,b = cv2.split(img1_bg)
#
#pos = signal.argrelextrema(hist, np.greater)
#peak = hist[pos]


#plt.plot(hist)



    
    '''
    out = np.zeros((img.shape[0], img.shape[1]), dtype = np.uint8)
    lowerBound = pos[1] - 5
    upperBound = pos[1] + 5
    cv2.inRange(img, lowerBound, upperBound, out)

    image, contours, hierarchy = \
    cv2.findContours(closing,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(image,contours,-1,(0,0,255),1)
    
    cv2.imshow('out', image)
    #print(min_value, average_value)
    '''


#pixelpoints = cv2.findNonZero(mask)
'''
cv2.imshow('1', img_binary)
cv2.imshow('2', img_close)
cv2.imshow('3', image)
#cv2.imshow('4',mask)
#plt.imshow(laplacian, cmap='gray')

#cv2.getStructuringElement(cv2.MORPH_CIRCLE,(5,5))

time_end = time.time()
print(time_end - time_start)
'''
