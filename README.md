### [Test videos](https://drive.google.com/drive/folders/1rCbAXBiJW5SK8wu499-4-jmYV4QqZ0oP?usp=sharing)

### Introduction

We working for tesla, volvo  made otonom systems, today. This systems consist of two parts. First part detection and second part direction. Lane and traffic lights detection systems create and guidance is made according to the data obtained. for this operations should using Raspberry Pi 4 (avaliable Raspberry Pi 3).   
 
In order for these stages to be tested, an RC Car infrastructure will be needed. The main products used are given in the link.
![](https://github.com/hhbulat/SelfDrivingCar/blob/main/pics/1.png?raw=true)

### Targets
In the picture above, the desired goals were given. The processes in the direction of achieving these goals will be explained step by step.

# Lane Tracking System
Lane Detection
----
![](https://github.com/hhbulat/SelfDrivingCar/blob/main/pics/2.png?raw=true)
As shown in the picture, we have a strip detection algorithm that will consist of 7 Stages.

- The image is converted to HSV format to be able to design a mask for white color. Images loaded in OpenCV are loaded in BGR format by default.
- Mask is applied according to the upper and lower values of the white color in HSV format.
- Canny function is applied to get the right parts. The Canny function detects all edges in the image.
- The area where the strips are located must be isolated. This is because other found white colors do not affect the algorithm.
- Coordinates of the correct parts of the isolated region are found using the HoughLinesP function.
- Since the number of correct parts found is quite large, it must be taken on average.
- After averaging and obtaining a single line, the middle line is drawn by finding the Middle points of the two lines for orientation.

As a result of the operations performed, lane detection was completed. The data obtained as a result of this process must be used in the routing section.
![](https://github.com/hhbulat/SelfDrivingCar/blob/main/pics/3.png?raw=true)
Direction
----
![](https://github.com/hhbulat/SelfDrivingCar/blob/main/pics/4.png?raw=true)
For a situation where two lanes are detected and one lane is detected, orientation should be performed by performing two separate calculations.

Modeling is shown above. In both cases, the correct parts of a-b will be considered as a right triangle and the angle will be found.


# Redirect Traffic Lights
The general logic is to detect edges by applying a mask to the red color, to be able to detect circles from the detected edges. While the system is efficient for a protip, there are places in everyday life where it can be inefficient.
![](https://github.com/hhbulat/SelfDrivingCar/blob/main/pics/1.png?raw=true)

[Link to test videos](https://drive.google.com/drive/folders/1rCbAXBiJW5SK8wu499-4-jmYV4QqZ0oP?usp=sharing)

Authors: [Linkedin by Hüseyin BULAT](https://tr.linkedin.com/in/hasan-h%C3%BCseyin-bulat-1a2208170?trk=public_profile_samename-profile) 
[Linkedin by Atakan Kara](https://www.linkedin.com/in/atakan-kara-671846216/)
