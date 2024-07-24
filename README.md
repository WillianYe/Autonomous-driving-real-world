## 自动驾驶小车实验
### 任务和实验效果
任务1，小车识别标志牌，进行转向和巡线：
![img](https://github.com/WillianYe/Autonomous-driving-real-world/blob/main/imgs/img1.png)
![img](https://github.com/WillianYe/Autonomous-driving-real-world/blob/main/imgs/gif1.gif)

任务2，小车检测并避开前方障碍物：
![img](https://github.com/WillianYe/Autonomous-driving-real-world/blob/main/imgs/img2.png)
![img](https://github.com/WillianYe/Autonomous-driving-real-world/blob/main/imgs/gif2.gif)
### 方法
+ task1.py实现标志牌识别
+ task2.py实现障碍物识别
+ calibration.py用于相机标定
+ driver.py包含通讯类
+ utils用于图像预处理等函数

1.场景和小车运动学建模
![img](https://github.com/WillianYe/Autonomous-driving-real-world/blob/main/imgs/img3.png)
![img](https://github.com/WillianYe/Autonomous-driving-real-world/blob/main/imgs/img4.png)
![img](https://github.com/WillianYe/Autonomous-driving-real-world/blob/main/imgs/img5.png)
2.图像识别算法

标志牌识别：综合比较hog+svm,yolov5,baidu-aip三种方法后，选择baidu-aip方法。

路口识别：一定距离内的黑色区域面积大于一定阈值即存在与车身线垂直道路，判断为分岔路口。

障碍物识别：检测到红色区域中心存在黄色区域即判定为要识别的障碍物。分割红色圆环，通过计算其大致像素半径大小来判断小车与障碍物之间距离。比较障碍物在红色圆环中心两侧一定范围内区域面积来判断障碍物的开口方向。


3.巡线算法

采用畸变校正与透视变换进行预处理；采用大津阈值分割进行二值化，同时只分割黑色区域，避免光照过亮时无法识别道路线；通过预瞄区域道路线和中线偏差进行误差检测；结合运动学模型和分级PID进行速度控制。




