import numpy as np 
import cv2 as cv
from typing import List

class ImageOrderFormat(str):
    CHW = 'CWC',  # Channel, Height, Width 
    CWH = 'CWH',   # Channel, Width , Height
    HWC = 'HWC',
    WHC = 'WHC'

class Langs(str):
    fa = 'fa-IR'

class SimpleSegmentator: 

    def __init__(self, lang: Langs =Langs.fa): 
        self.lang = lang

    def _get_index_of_natural_segment(self): 
        if self.lang == Langs.fa: 
            return (1,0)
        else: 
            raise NotImplementedError

    def _score(self, vals, indices): 
        normalize_vals = vals / np.max(vals)
        normalize_indices = np.abs(indices - len(indices)/2)
        normalize_indices = normalize_indices/ np.max(normalize_indices)
        #print(normalize_vals)
        #print(normalize_indices)

        value_effect = 0.60
        distance_effect = 0.40
        
        scores = value_effect*normalize_vals + distance_effect*normalize_indices

        return scores

    def _draw_segmentator_line(self, image, index):
        if self.lang == Langs.fa: 
            shape = image.shape
            print(shape)
            pt1 = (index, 0)
            pt2 = (index, shape[1]-1)
            image = cv.line(image, pt1, pt2, (255,255,0), 2, cv.LINE_4)
            return image
        else:
            NotImplementedError


    def __call__(self, image: np.ndarray,
            visualize=True, 
            image_format: ImageOrderFormat = ImageOrderFormat.CHW
            ) -> List[np.ndarray]:
        img = cv.cvtColor(image, cv.COLOR_RGB2GRAY)

        img_size = img.shape
        print("Image size is: {}".format(img_size))

        grads = cv.Laplacian(img, cv.CV_64F, ksize=5)
        #grads = cv.Sobel(img, cv.CV_64F, *self._get_index_of_natural_segment(), ksize=5)
        abs_grads = np.abs(grads)
        abs_grads = np.sum(abs_grads, axis=0)
        
        scores = self._score(abs_grads, np.arange(0, len(abs_grads),1))

        sorted_args = np.argsort(scores)
        #print(sorted_args)

        if visualize: 
            img = self._draw_segmentator_line(image, sorted_args[0])
            cv.imshow('visualize', img) 
            cv.waitKey(1000)

        return img

        