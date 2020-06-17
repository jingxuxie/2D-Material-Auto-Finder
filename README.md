# 2D-Material-Auto-Finder

## Introduction

This is a camera assistance tool designed with 2D material auto finder functions. 
You can use it to automatically find 2D materials on 
Si/SiO_2 chips together with an optical microscope with xyz scanning stage, also, you can just use it to edit local images, or 
connect it to a camera and measure the size and contrast of the sample. 

It has friendly user interface and you can use it easily by running the *.exe* file. I use PyQt5 to design the UI and use OpenCV to locate 
and recognize 2D materials, and use @jit to accelerate， then use PyInstallter to freeze the application into executables. 
The program now works fine on Win7 and Win10 (I didn't test it on MacOs).

This program is made during my visit at UC Berkeley in Prof. Feng Wang's group.

## Basic Usage
- Open files
- Zoom in
- Choose magnification
- Measure size and contrast
- Zoom out (press the right button)
![image](https://github.com/jingxuxie/2D-Material-Auto-Finder/blob/master/readme/start.gif)

- Gray mode
- Crop black frames
- Change contrast
- Custom contrast
![image](https://github.com/jingxuxie/2D-Material-Auto-Finder/blob/master/readme/contrast.gif)

- Draw lines
- Choose base line
- Measure angle
![image](https://github.com/jingxuxie/2D-Material-Auto-Finder/blob/master/readme/angle.gif)

- Edit images under 4k real time Live View
- Divide background and erase background inhomogenous
- Scale bar
- Setting calibrition
- Setting software background color

## 2D Layer Auto Finder
