import cv2 as cv
import numpy as np


class GridWarper():

    def __init__(self, xstep=8, ystep=8, random_area_ratio=0.1, same_shape=True, *args, **kwargs):
        self.xstep = xstep
        self.ystep = ystep
        self.mode = "bezier-bounderies"
        self.same_shape = same_shape
        
        print("Speaking from GridWarper")
        if kwargs.get('logger'): 
            self.logger = kwargs.get('logger')
        else: 
            self.logger = lambda x: print(x)

        if not self.same_shape:
            try: 
                self.output_dim = args.same_shape
            except:
                print("Falling back to default output shape") 
                self.output_dim = (1000,800,3)

        assert(random_area_ratio < 0.5 and random_area_ratio > 0.0)
        self.random_area_ratio = random_area_ratio
        self.random_output_dim = True

        self.visualize_conversion_points = False

    def path(self):
        pass

    def _get_random_point_in_range(self, x_range, y_range):
        return (np.random.randint(*x_range), np.random.randint(*y_range))

    def _get_random_area(self, area_code):
        rw = int(self.output_dim[1]*self.random_area_ratio)
        rh = int(self.output_dim[0]*self.random_area_ratio)
        w = self.output_dim[1]
        h = self.output_dim[0]
        if area_code == 'ul': # Upper left
            return ([0, rw], [0, rh])
        elif area_code == 'ur': # Upper right
            return ([w-rw, w], [0, rh])
        elif area_code == 'll': # Lower left
            return ([0, rw], [h-rh, h])
        elif area_code == 'lr': # Lower right
            return ([w-rw, w], [h-rh, h])
        else: 
            raise NotImplementedError

    def __call__(self, img: np.ndarray, pts: np.ndarray, background_img=None) -> np.ndarray:
        if self.same_shape:
            self.output_dim = img.shape  
            print("Image output dimension is set to", self.output_dim)  

        if self.random_output_dim:
            self.output_dim = (int(np.random.randint(800,1400)), int(np.random.randint(600, 1200)), 3)

        ul = self._get_random_point_in_range(*self._get_random_area('ul'))
        ur = self._get_random_point_in_range(*self._get_random_area('ur'))
        ll = self._get_random_point_in_range(*self._get_random_area('ll'))
        lr = self._get_random_point_in_range(*self._get_random_area('lr'))

        ow = img.shape[1]   
        oh = img.shape[0]
        oul = (0,0)
        our = (ow,0)
        oll = (0,oh)
        olr = (ow,oh) 

        srcPoints = np.zeros((4,2), dtype=np.float32)
        dstPoints = np.zeros((4,2), dtype=np.float32)
        srcPoints[0] = oul
        srcPoints[1] = our
        srcPoints[2] = olr
        srcPoints[3] = oll

        dstPoints[0] = ul
        dstPoints[1] = ur
        dstPoints[2] = lr
        dstPoints[3] = ll

        print("Src points")
        print(srcPoints)
        print("Dst points")
        print(dstPoints)
        print("From GridWarper", "####"*10)
        print(pts.shape)

        if len(self.output_dim) == 3 :
            self.output_dim = self.output_dim[::-1][1:]
        elif len(self.output_dim) == 2:
            self.output_dim = self.output_dim[::-1]
        else: 
            raise ValueError 

        persTrans = cv.getPerspectiveTransform(srcPoints, dstPoints)
        
        output = cv.warpPerspective(img, persTrans, dsize=self.output_dim)   

        # TODO: Fix scale 
        if background_img is not None: 
            background = cv.resize(background_img, self.output_dim[:2])
            mask = np.zeros(output.shape, dtype=np.uint8)

            dst_pts = dstPoints.astype(np.int32)
            #dst_pts = dst_pts[:,::-1]
            #dst_pts = dst_pts[:,:]
            dst_pts = np.array([dst_pts[:], dst_pts[0]])
            mask = cv.drawContours(mask, dst_pts, 0, (255,255,255), cv.FILLED)

            mask_inv = cv.bitwise_not(mask)
            print(mask_inv[:,:,0].shape, type(mask_inv))
            background = cv.bitwise_and(background, background, mask=mask_inv[:,:,0])
            paper = cv.bitwise_and(output, output, mask=mask[:,:,0])

            output = cv.add(paper, background)
        
        # Translating bounding boxes to new warped image
        num_bbox = pts.shape[0]
        pts_per_bbox = pts.shape[1]
        pts = pts.reshape((num_bbox*pts_per_bbox, pts.shape[2]))
        #pts = pts[:,::-1]

        pts = np.append(pts, np.ones((num_bbox*pts_per_bbox, 1), dtype=np.float32), axis=1)
        pts = pts.transpose()
        pts = np.matmul(persTrans, pts)
        pts = pts.transpose()
    
        pts = pts.reshape(num_bbox, pts_per_bbox, 3)
        for idx, box in enumerate(pts):
            for idx2, pt in enumerate(box):
                pts[idx][idx2] /= pts[idx][idx2][2] 
                
        pts = pts[:,:,:2]

        #pts = pts[:,::-1]
        pts = pts.astype(np.int)
        
        if self.visualize_conversion_points:
            for idx, point in enumerate([ul, ur, ll, lr]):
                output = cv.circle(output, point, 10, (255*(idx+1)/4,0,0), 10, cv.LINE_AA)
        
        return output, pts

