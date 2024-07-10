#!/usr/bin/env python
#-*- coding:utf-8 -*-
from aip import AipOcr  
import cv2
import os
import numpy as np
import time
from nor_img import *
from driver import driver
cap2 = cv2.VideoCapture(1) #前摄像头
AppID = "24230564"  #账号ID
APIkey = "zXsp0nLT1r0awG4VVyrYzohI"  #针对接口访问的授权方式
SecretKey = "T8x1FhVr3o8G2CaphVcZLe2cLNGVvKHP"  #密钥
  #常见图片格式
stop_flag=0
recognize_flag=0
left_flag=0
right_flag=0
turn_times=0
wait_flag = 0
back_flag=0
finish_flag=0
stop_times=0
car = driver()
e_i = 0
e_p = 0
e_d = 0
threshold=1500
low_rank = 1200
turn_times_threshold=22#12
tt = 0
a=u'左'
b=u'右'
client = AipOcr(AppID, APIkey, SecretKey)

cnt_high = 335
cnt_low = 325

vcnt_high = 40
vcnt_low = 600
w = 0
    
while True:
    st = time.time()
    _, frame2 = cap2.read()
    
    warp2 = warp(frame2)
    bina2, b2 = process(warp2) ###0.07
    #b2[cnt_low,:]=255
    #b2[cnt_high,:]=255
    cv2.imshow("bina2",b2)
    cv2.waitKey(1)
    #print(time.time()-st)
    #print(b2)
    #time.sleep(10)
    cnts = b2[cnt_low:cnt_high,:].sum()/255
    v_cnts = b2[450:,:].sum()/255
    cv2.imshow('frame2',frame2[120:300,200:440,:])
  
    print("cnts:"+str(cnts))
    print("v_cnts:"+str(v_cnts))
    if cnts>threshold and v_cnts > 700 and recognize_flag==0:
        stop_flag=1
        print('start')
    print('stop',stop_flag,'recog',recognize_flag)
    
    #if v_cnts < 200 and turn_times == 0:
        #l_s = 40
        #r_s = 40
    
    if stop_flag==0 and recognize_flag==0:   #十字路口检测
        print("move")
        max_v = np.zeros(5)     #正常巡线行驶
        max_l = np.zeros(5)
        for j in range(5):
            for i in range(0,560,40):
                tmp = bina2[j*60+180:j*60+240,i:i+120].mean()
                if tmp > max_v[j]:
                   max_v[j] = tmp
                   max_l[j] = i+60       
        error = 0
        cnt = 0        
        for i in range(5):
            
            if max_v[i] > 0:
                cnt = cnt + 1
                error = error + (max_l[i]-320) / 320.0

        if cnt > 0:
            error = error / cnt
        else:
            error = 0
            
        e_i = e_i + error
        e_d = error - e_p
        e_p = error
        if abs(error)<=0.25:
            v=75 * 0.5
            kp=15.0 * 1.4 
        elif abs(error)<=0.7:
            v=70 * 0.5
            kp=16.2 * 1.5 
        else:
            v=60 * 0.5
            kp=16.5 * 2.2 
        ki = 0.0
        kd = 42.0  * 1
        w = int( kp * error + ki * e_i + kd * e_d)        
        l_s = v - w
        r_s = v + w
        if l_s < 0:
            l_s = 5
        if r_s < 0:
            r_s = 5
        cirim, radius, pos = redf(frame2)
        print('radius:',radius,error)
        cv2.imshow('cir',cirim)
        
        if radius > 18:

            ma,fang=fxf(frame2, radius, pos)
            y,x = pos
            if y > radius and x > radius:
                simg = frame2[y-radius:y+radius,x-radius:x+radius,:]
                ye_r = yellowf(simg)
            else:
                ye_r = 0
            if fang ==1 and ye_r > 0:
                stop_flag=0
                recognize_flag=1
                left_flag = 1
                right_flag = 0
                turn_times_threshold=20
                print("left  @@@@@@@@@@@@@@@@@@@@@")
            elif fang==2 and ye_r > 0:
                stop_flag=0
                recognize_flag=1
                right_flag = 1
                left_flag = 0
                turn_times_threshold=20
                print("right  @@@@@@@@@@@@@@@@@@@")
                
    elif stop_flag==1 and recognize_flag==0:
        print("stop at crossroads.")
        l_s=0
        r_s=0
        stop_times=stop_times+1
        if stop_times<=5:
            #dimg = detect(frame2)
            cv2.imwrite('img'+str(stop_times)+'.jpg',frame2[120:300,200:440,:])#img2[160:260,150:450,:])
            fff = r'img'+str(stop_times)+'.jpg'
            with open(fff, 'rb') as f:
                content = f.read()
                api_result = client.basicGeneral(content)  # 调用通用文字识别接口
                result=[]
                print(api_result)
                try:
                    words_result = (i['words'] for i in api_result['words_result'])  # 文本内容
                except KeyError:
                    pass
                else:
                    result = '\n'.join(words_result)  # 图片的文本内容按照换行符拼接
            if result:       
                for i in result:
                    if i==a:
                        left_flag=1                   
                        stop_flag=0
                        recognize_flag=1
                        right_flag=0
                        turn_times_threshold=22
                        print("turn left.")
                        break
                    elif i==b:
                        right_flag=1
                        stop_flag=0
                        recognize_flag=1
                        left_flag=0
                        turn_times_threshold=22
                        print("turn right.")
                        break
        else:
            stop_times=0
            stop_flag=0
    elif stop_flag==0 and recognize_flag==1:
        print("recognize the signal.")
        turn_times=turn_times+1
        if left_flag==1:
            l_s=50
            r_s=6
            print("zuo")
        elif right_flag==1:
            l_s=6
            r_s=50
            print("you")
        if  turn_times>=turn_times_threshold and turn_times:
            recognize_flag=0
            turn_times=0
    #l_s = 0
    #r_s = 0
    car.set_speed(l_s, r_s)
    print('time',time.time()-st,'error',error,'l_s',l_s,'r_s',r_s)
    
