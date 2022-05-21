
import os

import cv2 as cv
import numpy as np 
from glob import glob 

from Segmentator import SimpleSegmentator

base_path = os.path.dirname(__file__)
test_img_path = 'test_imgs'

seg = SimpleSegmentator()
output_width = 360
final = np.zeros((1,output_width,3), dtype=np.uint8)

for file in glob(os.path.join(base_path, test_img_path,'*')):
    print(file)
    img = cv.imread(file)
    output = seg(img)
    shape = output.shape
    print(shape)
    #output = output.reshape(int((shape[0]/shape[1])*output_width),output_width,3)
    output = cv.resize(output, (output_width, int((shape[0]/shape[1])*output_width)))
    print(output.shape)
    print("Final Shape", final.shape)
    final = np.concatenate((output, final), axis=0)

cv.imwrite('./output.jpg', final)
