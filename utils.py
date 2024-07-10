# -*- coding: UTF-8 -*-
import cv2
import numpy as np


"""
DIM=(640, 480)
K=np.array([[499.05021523540756, 0.0, 333.3412892374512], [0.0, 483.81654015414097, 242.69653225978055], [0.0, 0.0, 1.0]])
D=np.array([[-0.869900379788289], [1.3590213730501584], [-1.820747530181677], [1.1118149732028872]])
"""
DIM=(640, 480)
K=np.array([[-5198.347002578433, -0.0, 322.2498961240888], [0.0, -5256.783989831324, 245.62154951821046], [0.0, 0.0, 1.0]])
D=np.array([[-128.930840598615], [22976.1473011057], [-2773014.037028126], [143281119.86853617]])

def detect_circle(image):

    _, contours, hierarchy = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    p = 0
    dmin = 99999999
    if len(contours) > 0:
        boxes = [cv2.boundingRect(c) for c in contours]
        for i,box in enumerate(boxes):
            x, y, w, h = box
            if (x+w/2 - 320)*(x+w/2 - 320) + (y+h/2 - 300)*(y+h/2 - 300) < dmin and w*h > 500:
                dmin = (x+w/2 - 320)*(x+w/2 - 320) + (y+h/2 - 300)*(y+h/2 - 300)
                p = i
        
        x, y, w, h = boxes[p]
        
        x = int(x + w/2)
        y = int(y + h/2)
        r = max(h, w)
        r = int(r/2 + 4)
        
        simg = image[y-r:y+r,x-r:x+r]

        return image , r , (y,x)
    else:
        return image , 0, (180,270)
    
def redf(frame):

    red_lower=np.array([0,231,40])
    red_upper=np.array([12,255,128])
    frame=frame[120:480,60:600,:]
    frame=cv2.GaussianBlur(frame,(5,5),0)                    
    hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    mask1=cv2.inRange(hsv,red_lower,red_upper)

    im, r, pos = detect_circle(mask1)
    return im, r, pos

def fxf(frame, r, pos) :
    qita_lower=np.array([17,66,125])
    qita_upper=np.array([45,229,255])
    frame=frame[120:480,60:600,:]
    frame=cv2.GaussianBlur(frame,(5,5),0)                    
    hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    mask3=cv2.inRange(hsv,qita_lower,qita_upper)
    
    left = mask3[:,pos[1]-4*r:pos[1]].sum()
    right = mask3[:,pos[1]:pos[1]+4*r].sum()
    
    #mask3[:,pos[1]] = 255
    #mask3[:,pos[1]-4*r] = 255
    #mask3[:,pos[1]+4*r] = 255

    print('left:', left, 'right', right)
    if right > left:
        #print('turn left')
        return mask3, 1
    else:
        #print('turn right')
        return mask3, 2
    
def yellowf(frame):

    yellow_lower=np.array([19,228,63])
    yellow_upper=np.array([29,255,255])
    #frame=frame[120:480,60:600,:]
    #frame=cv2.GaussianBlur(frame,(5,5),0)                    
    hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    mask=cv2.inRange(hsv,yellow_lower,yellow_upper)

    im, r, pos= detect_circle(mask)
    return r

def undistort_up(img_path,scale=0.5,imshow=False):
    img = cv2.imread(img_path)
    dim1 = img.shape[:2][::-1]  #dim1 is the dimension of input image to un-distort
    assert dim1[0]/dim1[1] == DIM[0]/DIM[1], "Image to undistort needs to have same aspect ratio as the ones used in calibration"
    if dim1[0]!=DIM[0]:
        img = cv2.resize(img,DIM,interpolation=cv2.INTER_AREA)
    Knew = K.copy()
    if scale:#change fov
        Knew[(0,1), (0,1)] = scale * Knew[(0,1), (0,1)]
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), Knew, DIM, cv2.CV_16SC2)
    undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    if imshow:
        cv2.imshow("undistorted", undistorted_img)
    cv2.imwrite('unfisheyeImage_up.png', undistorted_img)
    return undistorted_img


def dd(image):


    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    l_blue = np.array([[0,43,46]])
    h_blue = np.array([12,255,255])

    mask = cv2.inRange(hsv, l_blue, h_blue)
    res = cv2.bitwise_and(image, image, mask = mask)
    
    black1 = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
    blur1 = cv2.GaussianBlur(black1,(5,5),0)

    ret1,th1 = cv2.threshold(blur1,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    
    return th1


def detect(image):

    t = dd(image)
    
    kernel = np.ones((5, 5), np.uint8)
    dilation = cv2.erode(t, kernel, iterations=1)
    dilation = cv2.dilate(dilation, kernel, iterations=2)
    #cv2.imshow('di',dilation)
    
    _,contours,_ = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    p = 0
    dmin = 99999999
    if len(contours) > 0:
        #cv2.boundingRect()返回轮廓矩阵的坐标值，四个值为x, y, w, h， 其中x, y为左上角坐标，w,h为矩阵的宽和高
        print(len(contours))
        boxes = [cv2.boundingRect(c) for c in contours]
        for i,box in enumerate(boxes):
            x, y, w, h = box
            #绘制矩形框对轮廓进行定位
            if (x+w/2 - 320)*(x+w/2 - 320) + (y+h/2 - 300)*(y+h/2 - 300) < dmin:
                dmin = (x+w/2 - 320)*(x+w/2 - 320) + (y+h/2 - 300)*(y+h/2 - 300)
                p = i
            #cv2.rectangle(im, (x, y), (x+w, y+h), (153, 153, 0), 2)
            # if a == 18:
                # print("location:", x+w/2, "," , y+h/2)
        # if a == 18:
            # print("###############")
        
        x, y, w, h = boxes[p]
        
        x = int(x + w/2)
        y = int(y + h/2)
        r = max(h, w)
        r = int(r/2 + 10)
        
        simg = image[y-r:y+r,x-r:x+r]
        
        return simg
    else:
        return image

def undistort(img):

    img = cv2.resize(img, DIM)
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, DIM,cv2.CV_16SC2)
    undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)    

    return undistorted_img

def warp(img):
    x = 300
    y = 180
    img_info = img.shape
    height = img_info[0]
    width = img_info[1]
    #获取原图像的左上角，左下角，右上角三个点的坐标  （三点确定图像所在二维平面）
    pts1 = np.float32([[250, 280],[400,280],[0, height],[width,height]])
    
    pts2 = np.float32([[0, 0],[width,0],[0, height],[width,height]])
    # 生成透视变换矩阵；进行透视变换
    M = cv2.getPerspectiveTransform(pts1, pts2)
    dst = cv2.warpPerspective(img, M, (width,height))
    
    #cv2.imshow('dst',dst)

    return dst


def process(img):
    redLower = np.array([0, 0, 0])
    redUpper = np.array([180, 255, 46])
    blacks = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    blur = cv2.GaussianBlur(blacks,(5,5),0)
    black = cv2.inRange(blur, redLower, redUpper)
    ret,th = cv2.threshold(black,0,255,cv2.THRESH_BINARY)#+cv2.THRESH_OTSU)
    canny = cv2.Canny(th, 50, 150)
    
    return canny, th

#while(True):
if __name__=='__main__':
    
    for cnt in range(1,9):
        #cnt = 1
    
        img = cv2.imread('./imgs/img_'+str(cnt)+'_calib.jpg')

        warp_img = warp(img)
        
        th, ca = process(warp_img)
        
        cv2.imwrite('./imgs/img_edge_'+str(cnt)+'.jpg',ca)
        cv2.imwrite('./imgs/img_black_'+str(cnt)+'.jpg',th)
    
    print("yes")
    
