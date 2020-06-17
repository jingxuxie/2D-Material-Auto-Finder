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
- Divide background and eliminate background inhomogenous
- Scale bar
- Setting calibrition
- Setting software background color

## 2D Layer Auto Finder

Click the last button in toolbar. Then choose material (graphene or TMD), and thickness of substrate (285 nm or 90 nm), and the magnification to use (5x or 10x). Recommend 5x for graphene and 10x for TMD. To use the auto finder, of course, you need an optical microscope with a programmable xyz scanning stage.

The program will first do auto focus for three points on the chip to determine the plane, since we assume the chip is flat and it may tilt for some reason. Then it controls the stage to scan the plane and take photos. Next, the finder will work on the photos to locate the 2D layers and identify their thickness by calculating the contrast.

Before using this function, you need to capture background pictures to eliminate background inhomogenous. This is highly important and background inhomogenous will leads to decreasing accuracy dramatically. Also, you need to fix the settings of your camera and the light source. To yield good results, make sure that in gray mode, the histogram peaks around 130, which indicates a proper environment brightness.

Here are some examples of finding results. The green frames locate the layers and the red dot at the top right coner indicate the relative position of the chip.

- Graphene
![image](https://github.com/jingxuxie/2D-Material-Auto-Finder/blob/master/readme/gr.bmp)

- WS2
![image](https://github.com/jingxuxie/2D-Material-Auto-Finder/blob/master/readme/WS2.jpg)
