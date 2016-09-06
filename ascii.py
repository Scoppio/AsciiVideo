'''

Creates an ascii art video from an arbitrary video
Created on 10 aug 2016
 
@author: Lucas Coppio
Ascii art based on the work of Steven Kay

MIT License - look it up on google.

'''

from PIL import Image
from bisect import bisect
import numpy as np
import argparse
import random
import cv2

def textSize(text, fontFace, fontScale, thickness):
    '''
    Compute text size in image relative by fontscale and thickness
    '''
    text_size, ymin = cv2.getTextSize(text, fontFace, fontScale, thickness)
    width, height = text_size
    return width, height, ymin

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=False, default="",
    help="input video")
ap.add_argument("-o", "--output", required=False, default="output1.mp4",
    help="output file mp4")
ap.add_argument("-s", "--scale", required=False, default=1, type= int,
    help="scale the video")
ap.add_argument("-r", "--reverse_colors", required=False,  action="store_true",
    help="reverse colors")
ap.add_argument("-v", "--verbose", required=False,  action="store_true",
    help="Adds verbosity")
args = vars(ap.parse_args())

# greyscale.. the following strings represent
# 7 tonal ranges, from lighter to darker.
# for a given pixel tonal level, choose a character
# at random from that range.
 
greyscale = [
            " ",
            " ",
            ".,-",
            "_ivc=!/|\\~",
            "gjez2]/(YL)t[+T7Vf",
            "mdK4ZGbNDXY5P*Q",
            "W8KMA",
            "#%$"
            ]
 
# Zonebounds control the tonal band for the grayscale images

zonebounds=[36,72,108,144,180,216,252]
 
# open image and resize
# experiment with aspect ratios according to font

reverse_colors = args["reverse_colors"]


w, h, ymin = textSize("O", fontFace = cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5/args["scale"], thickness=1)
h = h + 6

# OpenCV start
cap = cv2.VideoCapture(args["input"])
orig_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) // args["scale"])
orig_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) // args["scale"])
orig_fps = cap.get(cv2.CAP_PROP_FPS)
fourcc = cv2.VideoWriter_fourcc(*'H264')

# Frame setup
width = int(orig_width // 8)
height = int(orig_height // 14)
video_size = (width*w, height*h)

# Output video!!!
out = cv2.VideoWriter(args["output"], fourcc, orig_fps, video_size, False)


if args["verbose"]: 
    print("Video size: {} Reverse colors:".format(video_size,reverse_colors))

while cap.isOpened(): 

    ret, frame = cap.read()

    if not ret: break

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = frame.astype("uint8")

    if reverse_colors:
        frame = np.ones(frame.shape)*255 - frame

    # uncomment the following line if you want to see the video it is processing
    # cv2.imshow(args["input"],frame)

    # unfortunatelly I am too lazy right now to turn the numpy.array that is the frame into a format that is understood by PIL
    cv2.imwrite("~temp.png", frame)
    
    #Yeah, this level of lazyness, if you want to 
    im=Image.open("~temp.png")


    im=im.resize((width, height),Image.BILINEAR)
    im=im.convert("L") # convert to mono
     
    # now, work our way over the pixels
    # build up str     

    image_ascii=""
    ascii_list = []
    for y in range(0,im.size[1]):
        for x in range(0,im.size[0]):
            lum = 255 - im.getpixel((x,y))
            row = bisect(zonebounds,lum)
            possibles = greyscale[row]
            ascii_list.append( [ possibles[random.randint(0,len(possibles)-1)]])
            image_ascii = image_ascii + possibles[random.randint(0,len(possibles)-1)]

        image_ascii = image_ascii + "\n"

    if args["verbose"]: print(image_ascii)

    img = np.zeros([height*h, width*w]).astype('uint8')
    font = cv2.FONT_HERSHEY_SIMPLEX

    row, col = 0, 0
    image_ascii = image_ascii.split('\n')

    for line in image_ascii:
        for letter in line:
            cv2.putText(img, letter, ( w*col, h//2+h*row), font, 0.5 / args["scale"] , (255,255,255), 1, cv2.LINE_AA)
            col += 1

        col = 0
        row += 1
        
    cv2.imshow(args["input"],img)
    cv2.imwrite("~frame_ascii.png", img)
    
    out.write(img)

    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

cap.release()
out.release()