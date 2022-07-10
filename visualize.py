#!/usr/bin/python3

import cv2 as cv
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--img", type=str)
parser.add_argument("--bbox", type=str)

args = parser.parse_args()

winname = 'test'
cv.namedWindow(winname, cv.WINDOW_NORMAL)

img = cv.imread(args.img)

scale = (225.5/72)

with open(args.bbox, 'r') as file:
    bboxes = file.readlines()
    for bbox in bboxes: 
        elems = [int(float(elem)) for elem in bbox.split(',')]

        x = int(elems[0]*scale)
        y = int(elems[1]*scale)
        w = int(elems[2]*scale)
        h = int(elems[3]*scale)

        ul = (x,y)
        ur = (x+w,y)
        ll = (x,y+h)
        lr = (x+w,y+h)

        points = [ul, ur, lr, ll]
        for idx, point in enumerate(points):
            vertex_color = (255,0,0)
            line_color = (255,0,0)
            img = cv.circle(img, point, 4, vertex_color, 2, cv.LINE_AA)
            img = cv.line(img, points[idx], points[(idx+1)%4], line_color, 2, cv.LINE_AA)

cv.imshow(winname, img)
cv.waitKey(0)

