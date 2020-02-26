# -*- coding: utf-8 -*-
"""
Created on Sun Feb  9 20:56:22 2020

@author: HP
"""

import win32gui, win32api, win32con
from win32gui import PyMakeBuffer,SendMessage, PyGetBufferAddressAndLen, PyGetString,\
                    GetDlgItemText
import time
import pywinauto
from pywinauto.application import Application

window_name = 'BX2 '
hwnd = win32gui.FindWindow(None, window_name)


clsname = win32gui.GetClassName(hwnd)

win32gui.SendMessage(hwnd, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)
win32gui.SetForegroundWindow(hwnd)

hwndChildList = []
win32gui.EnumChildWindows(hwnd, lambda hwnd, param: param.append(hwnd), hwndChildList)
#print(hwndChildList)

for child_hwnd in hwndChildList:
    classname = win32gui.GetClassName(child_hwnd)
    name = win32gui.GetWindowText(child_hwnd)
    if name == 'Focus' and classname == '#32770':
        focus_hwnd = child_hwnd
        print('123')
    if name == 'Position':
        print('456')
        
#    print(classname)
    if classname == 'SysTabControl32':
        left, top, right, bottom = win32gui.GetWindowRect(child_hwnd)
        print(left, top, right, bottom)
        print(child_hwnd)
        print('yes!')

hwnd = focus_hwnd
hwndChildList = []
win32gui.EnumChildWindows(hwnd, lambda hwnd, param: param.append(hwnd), hwndChildList)
name = win32gui.GetWindowText(hwndChildList[6])
print(name)    

edit_hwnd = hwndChildList[8]
edit = pywinauto.controls.win32_controls.EditWrapper(edit_hwnd)
edit.set_text(str(1000))
button = pywinauto.controls.win32_controls.ButtonWrapper(hwndChildList[4])
button.click()
''' 
win32api.SetCursorPos([left + 100,top + 10])
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP | win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)

time.sleep(1)
win32api.SetCursorPos([left + 130,top + 250])
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP | win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)

time.sleep(1)
win32api.SetCursorPos([left + 80,top + 240])
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP | win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
'''

'''
time.sleep(1)
win32api.SetCursorPos([left + int((right-left)/5*2),top + 10])
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP | win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(1)
win32api.SetCursorPos([left + int((right-left)/15),top + int((bottom-top)/2*0.96)])
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP | win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(1)
window_name = 'Soft Key'
hwnd = win32gui.FindWindow(None, window_name)
print(hwnd)

hwndChildList = []
win32gui.EnumChildWindows(hwnd, lambda hwnd, param: param.append(hwnd), hwndChildList)
#for hwnd in hwndChildList:
#    print(win32gui.GetWindowText(hwnd))
'''
'''
time.sleep(1)
win32api.SetCursorPos([left + 130,top + 70])
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP | win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
#win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

time.sleep(1)
win32api.SetCursorPos([left + 130,top + 115])
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP | win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
#win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

time.sleep(1)
win32api.SetCursorPos([left + 130,top + 160])
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP | win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
'''
'''
time.sleep(1)
win32api.SetCursorPos([left + 130,top + 200])
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP | win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

time.sleep(1)
win32api.SetCursorPos([left + 130,top + 240])
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP | win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)


'''
#edit_hwnd = hwndChildList[8]
#edit = pywinauto.controls.win32_controls.EditWrapper(edit_hwnd)
#edit.set_text(str(1000))
#button = pywinauto.controls.win32_controls.ButtonWrapper(hwndChildList[4])
#button.click()
'''
left, top, right, bottom = win32gui.GetWindowRect(focus_hwnd)

focus_button = pywinauto.controls.win32_controls.ButtonWrapper(hwndChildList[0])
check_state = focus_button.get_check_state()

for i in range(1):
    time.sleep(1)
    button = pywinauto.controls.win32_controls.ButtonWrapper(hwndChildList[4])
    button.click()
#    win32api.SetCursorPos([left + 230,top + 100])
#    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP | win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
'''
