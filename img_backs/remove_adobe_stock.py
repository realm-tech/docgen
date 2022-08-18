from glob import glob 
import cv2 as cv 

# This is written since the adobe is by default adding some text to the images

for img_path in glob('./*.jpeg'): 
    img = cv.imread(img_path)
    shape = img.shape
    img = img[:, shape[1]//20:, :]
    
    cv.imwrite(img_path, img)
    
