# -*- coding: utf-8 -*-
"""
Created on Sun Feb  2 20:04:38 2020

@author: HP
"""

import win32gui, win32api, win32con
from win32gui import PyMakeBuffer,SendMessage, PyGetBufferAddressAndLen, PyGetString,\
                    GetDlgItemText
import time
import pywinauto
from pywinauto.application import Application

window_name = 'PriorTerminal'
hwnd = win32gui.FindWindow(None, window_name)

hwndChildList = []
win32gui.EnumChildWindows(hwnd, lambda hwnd, param: param.append(hwnd), hwndChildList)
print(hwndChildList)


for child_hwnd in hwndChildList:
    classname = win32gui.GetWindowText(child_hwnd)
    if classname == 'menuStrip1':
        menubar_hwnd = child_hwnd
    print(classname)
    if classname == 'SysTabControl32':
        print('yes!')
'''
char = 'L 2000'
for _ in char:
    win32api.SendMessage(hwndChildList[-1], win32con.WM_CHAR, ord(_), 0)
win32api.SendMessage(hwndChildList[-1], win32con.WM_CHAR, 13, 0)
#a = win32gui.GetWindowText(hwndChildList[-1])
#a = GetDlgItemText(hwndChildList[-1])
'''

menubar_hwnd = hwndChildList[2]
win32gui.SendMessage(hwnd, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)
left, top, right, bottom = win32gui.GetWindowRect(menubar_hwnd)
print(left, top, right, bottom)
win32api.SetCursorPos([left + int((right - left)/5*3),top + int((bottom-top)/2)])
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP | win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)


edit_text_hwnd = hwndChildList[-1]
edit_text = pywinauto.controls.win32_controls.EditWrapper(edit_text_hwnd)

list_box_hwnd = hwndChildList[-2]
list_box = pywinauto.controls.win32_controls.ListBoxWrapper(list_box_hwnd)

def pause():
    count = 0
    time_start = time.time()
    while count <50:
        b = list_box.item_texts()
        if b[-1] == 'R':
            time.sleep(0.01)
            time_end = time.time()
            print(time_end - time_start)
            break
        else:
            time.sleep(0.05)
            count += 1

i = 0
j = 0
'''
line = 1
while i < 10000:
    j = 0
    while j < 10000:
        j += 1000
        if line%2 == 1:
            edit_text.set_text('L ' +str(1000))
        else:
            edit_text.set_text('R ' +str(1000))
        win32api.SendMessage(edit_text_hwnd, win32con.WM_CHAR, 13, 0)
        pause()
        #edit_text.set_text('PS')
        #win32api.SendMessage(edit_text_hwnd, win32con.WM_CHAR, 13, 0)
        
    line += 1    
    i += 1000
    edit_text.set_text('B '+str(1000))
    win32api.SendMessage(edit_text_hwnd, win32con.WM_CHAR, 13, 0)
    pause()
    
'''        





            

print(time_end - time_start)
'''
hwnd = hwndChildList[-3]
dlg = win32gui.FindWindowEx(hwnd, None, 'Connect', None)
menu = win32gui.GetMenu(hwnd)
#menu1 = win32gui.GetSubMenu(menu, 1)



app = Application()
app.connect(handle = 198250)
#app.connect(path = r"C:\Program Files\Prior Scientific\Prior Software\PriorTerminal.exe")

#app.WindowSpecificati1on.print_control_identifiers()
'''

'''
subHandle = hwndChildList[-2]
bufSize = 10000# = win32api.SendMessage(subHandle, win32con.WM_GETTEXTLENGTH, 0, 0) +1
# 利用api生成Buffer
strBuf = win32gui.PyMakeBuffer(bufSize)
print(strBuf)

# 发送消息获取文本内容
# 参数：窗口句柄； 消息类型；文本大小； 存储位置
length = win32gui.SendMessage(subHandle, win32con.WM_GETTEXT, bufSize, strBuf)
# 反向内容，转为字符串
# text = str(strBuf[:-1])
address, length = win32gui.PyGetBufferAddressAndLen(strBuf)
text = win32gui.PyGetString(address, length)
# print('text: ', text)
'''


'''
b = win32gui.GetDlgItem(hwnd, 22941298)
dlg = win32gui.FindWindowEx(hwnd, None, 'Connect', None)
print(dlg)
menu = win32gui.GetMenu(hwnd)
#win32gui.Get
#menu1 = win32gui.GetSubMenu(menu, 0)
'''