import numpy as np 
import cv2 as cv 

from typing import List, Any

def cairopdfunits2cvpix(poses: np.ndarray, page_height, zoom=1, dpi=300):
    """_summary_

    Args:
        poses (np.ndarray): _description_
    """

    for idx, pos in enumerate(poses): 
        poses[idx][1] = page_height - poses[idx][1] 
        poses[idx][3] = page_height - poses[idx][3]
    
    pdfunit2csspix = (dpi/96)*(96/72)*zoom

    #poses = pdfunit2csspix*poses
    for idx, pos in enumerate(poses): 
        for i, coord in enumerate(pos): 
            pos[i] *= pdfunit2csspix
        
        poses[idx] = pos

    return poses

def poses2bboxes(poses: List[Any], page_height: float, zoom: float) -> np.ndarray: 
    print("Page heigth is set to", page_height)
    poses = poses[0]

    poses = cairopdfunits2cvpix(poses, page_height, zoom)
    wbboxes = np.zeros((len(poses), 4, 2), dtype=np.float32)

    for idx, pos in enumerate(poses):
        print(idx)
        w = pos[2] - pos[0]
        h = pos[3] - pos[1]
        # Clock-wise order from upper-left
        wbboxes[idx,0] =  (pos[0], pos[1]) # Upper left
        wbboxes[idx,1] =  (pos[0]+w, pos[1]) # Upper right
        wbboxes[idx,2] =  (pos[0]+w, pos[1]+h) # Lower right
        wbboxes[idx,3] =  (pos[0], pos[1]+h) # Lower left

    return wbboxes

def drawbboxes(img: np.ndarray, bboxes: np.ndarray, color=(0,0,0)) -> np.ndarray: 

    line_size = 4
    # Iterating over all word bboxes
    for bbox in bboxes: 
        # Iterating over all points in a single bbox
        for pt_idx, pt in enumerate(bbox): 
            img = cv.circle(img, tuple(pt), 3, color, line_size, cv.LINE_8)
            img = cv.line(img, tuple(pt), tuple(bbox[(pt_idx+1)%4]), color, line_size, cv.LINE_8)
    
    return img

 