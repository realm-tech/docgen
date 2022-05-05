import numpy as np
import cv2 as cv 
from glob import glob

from warper import GridWarper

gridWarper = GridWarper()
winname = 'test'
cv.namedWindow(winname, cv.WINDOW_NORMAL)

for file in glob("./test/*.png"):
    pts = np.random.rand(1,4,2)
    img = cv.imread(file)
    output, pts = gridWarper(img,pts)

    cv.imshow(winname, output)
    cv.waitKey(0)
