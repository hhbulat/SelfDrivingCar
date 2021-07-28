import cv2,math,time
import numpy as np
import matplotlib.pyplot as plt
import RPi.GPIO as GPIO




# The frame taken from the camera is converted to HSV format and a mask is applied to the color tones. The edges are detected with the applied mask.
def edges_detect(frame):
    HSV = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    lower_white= np.array([0,0,65])
    upper_white= np.array([180,255,255])
    mask = cv2.inRange(HSV,lower_white,upper_white)
    edges = cv2.Canny(mask,200,400)
    
    return edges

# Masking is done completely according to the location of the strips.
def ROI(edges):
    height,width = edges.shape
    mask = np.zeros_like(edges)
    polygon = np.array([[(0, height * 1 / 2),(width, height * 1 / 2),(width, height),(0, height),]], np.int32)
    cv2.fillPoly(mask,polygon,255)
    mask_edges = cv2.bitwise_and(edges,mask)
    
    return mask_edges

# The coordinates of the strip segments are obtained with the HoughLinesP format.
def detect_line_coordinats(mask_edges):
    line_coordinats = cv2.HoughLinesP(mask_edges,1,np.pi/180,10,np.array([]),minLineLength=8,maxLineGap=4)
    return line_coordinats


# Line segments are drawn according to the coordinates found (x1,y1,x2,y2).
def lines_draw(frame,lines,line_color=(0,255,0),line_width=10):
    line_zero_image = np.zeros_like(frame)
    if lines is not None:
        for i in lines:
            for x1,y1,x2,y2 in i:
                cv2.line(line_zero_image, (x1, y1), (x2, y2), line_color, line_width)
    line_zero_image = cv2.addWeighted(frame,0.8,line_zero_image,1,1)
    return line_zero_image
# Create point for found slope and intercept (graph 0 point).
def points_make(frame, line):
    height, width, _ = frame.shape
    slope, intercept = line
    y1 = height  # bottom of the frame
    y2 = int(y1 * 1 / 2)  # make points from middle of the frame down

    # bound the coordinates within the frame
    x1 = max(-width, min(2 * width, int((y1 - intercept) / slope)))
    x2 = max(-width, min(2 * width, int((y2 - intercept) / slope)))
    return [[x1, y1, x2, y2]]

# More than one line segment detected for each lane. For this, a single line is obtained by taking the average.
def avg_slope_intercept(frame, line_coordinats):
    lines = []
    if line_coordinats is None:
        return lines
    height, width, _ = frame.shape
    left_fit = []
    right_fit = []

    boundary = 1/3
    left_boundary = width * (1 - boundary)
    right_boundary = width * boundary

    for line_coordinat in line_coordinats:
        for x1, y1, x2, y2 in line_coordinat:
            if x1 == x2:
                continue
            fit = np.polyfit((x1, x2), (y1, y2), 1)
            slope = fit[0]
            intercept = fit[1]
            if slope < 0:
                if x1 < left_boundary and x2 < left_boundary:
                    left_fit.append((slope, intercept))
            else:
                if x1 > right_boundary and x2 > right_boundary:
                    right_fit.append((slope, intercept))

    left_fit_avg = np.average(left_fit, axis=0)
    if len(left_fit) > 0:
        lines.append(points_make(frame, left_fit_avg))

    right_fit_avg = np.average(right_fit, axis=0)
    if len(right_fit) > 0:
        lines.append(points_make(frame, right_fit_avg))
    
    return lines

def calculate_angle(frame, lines):
    if len(lines) == 0:
        return -90
    height, width, _ = frame.shape
    if len(lines) == 1:
        x1, _, x2, _ = lines[0][0]
        x_offset = x2 - x1
    else:
        _, _, left_x2, _ = lines[0][0]
        _, _, right_x2, _ = lines[1][0]
        camera_mid_offset = 0.02 # 0.0 means car pointing to center, -0.03: car is centered to left, +0.03 means car pointing to right
        mid = int(width / 2 * (1 + camera_mid_offset))
        x_offset = (left_x2 + right_x2) / 2 - mid


    y_offset = int(height / 2)

    angle_radian = math.atan(x_offset / y_offset)  # angle (in radian) 
    angle_deg = int(angle_radian * 180.0 / math.pi)  # angle (in degrees) 
    real_angle = angle_deg + 90  # this is the steering angle

    return real_angle

# Stabilization is done because the calculated steering angles are not completely stable.
def stabilize_angle(duty,real_angle, new_angle, number_of_lines, two_lines_max_deviation=5, one_lines_max_deviation=1):
    if number_of_lines == 2 :
        # if both lane lines detected, then we can deviate more
        max_angle_deviation = two_lines_max_deviation
    else :
        # if only one lane detected, don't deviate too much
        max_angle_deviation = one_lines_max_deviation
    
    angle_deviation = new_angle - real_angle
    if abs(angle_deviation) > max_angle_deviation:
        stabilized_angle = int(real_angle + max_angle_deviation * angle_deviation / abs(angle_deviation))
    else:
        stabilized_angle = new_angle
    return stabilized_angle

def direction(angle,in1,in2,pwm0,pwm1):
    x=55
    y=53
    if angle <= 85 and angle > 80:
        way = "LEFT" 
        GPIO.output(in1,GPIO.HIGH)
        GPIO.output(in2,GPIO.LOW)
        pwm1.ChangeDutyCycle(y)
        pwm0.ChangeDutyCycle(6.8)
    elif angle <= 80 and angle > 75:
        way = "LEFT" 
        GPIO.output(in1,GPIO.HIGH)
        GPIO.output(in2,GPIO.LOW)
        pwm1.ChangeDutyCycle(y)
        pwm0.ChangeDutyCycle(6.5)
    elif angle <= 75 and angle > 70:
        way = "LEFT"
        GPIO.output(in1,GPIO.HIGH)
        GPIO.output(in2,GPIO.LOW)
        pwm1.ChangeDutyCycle(y)
        pwm0.ChangeDutyCycle(6.2)
    elif angle <= 70 and angle > 65:
        way = "LEFT" 
        GPIO.output(in1,GPIO.HIGH)
        GPIO.output(in2,GPIO.LOW)
        pwm1.ChangeDutyCycle(y)
        pwm0.ChangeDutyCycle(5.9)
    elif angle <= 65 and angle > 60:
        way = "LEFT" 
        GPIO.output(in1,GPIO.HIGH)
        GPIO.output(in2,GPIO.LOW)
        pwm1.ChangeDutyCycle(y)
        pwm0.ChangeDutyCycle(5.7)
    elif angle <= 60 and angle > 55:
        way = "LEFT" 
        GPIO.output(in1,GPIO.HIGH)
        GPIO.output(in2,GPIO.LOW)
        pwm1.ChangeDutyCycle(y)
        pwm0.ChangeDutyCycle(5.6)
    elif angle <= 55 and angle > 50:
        way = "LEFT" 
        GPIO.output(in1,GPIO.HIGH)
        GPIO.output(in2,GPIO.LOW)
        pwm1.ChangeDutyCycle(y)
        pwm0.ChangeDutyCycle(5.3)
    elif angle <= 50 and angle > 45:
        way = "LEFT" 
        GPIO.output(in1,GPIO.HIGH)
        GPIO.output(in2,GPIO.LOW)
        pwm1.ChangeDutyCycle(y)
        pwm0.ChangeDutyCycle(5)
    elif angle <= 45 and angle > 40:
        way = "LEFT" 
        GPIO.output(in1,GPIO.HIGH)
        GPIO.output(in2,GPIO.LOW)
        pwm1.ChangeDutyCycle(y)
        pwm0.ChangeDutyCycle(4.7)
    elif angle < 40:
        way = "LEFT" 
        GPIO.output(in1,GPIO.HIGH)
        GPIO.output(in2,GPIO.LOW)
        pwm1.ChangeDutyCycle(y)
        pwm0.ChangeDutyCycle(4.7)
    elif angle > 95 and angle < 100:
        way = "RIGHT" 
        GPIO.output(in1,GPIO.HIGH)
        GPIO.output(in2,GPIO.LOW)
        pwm1.ChangeDutyCycle(y)
        pwm0.ChangeDutyCycle(7.3)
    elif angle >= 100 and angle <105:
        way = "RIGHT" 
        GPIO.output(in1,GPIO.HIGH)
        GPIO.output(in2,GPIO.LOW)
        pwm1.ChangeDutyCycle(y)
        pwm0.ChangeDutyCycle(7.6)
    elif angle >= 105 and angle < 110:
        way = "RIGHT" 
        GPIO.output(in1,GPIO.HIGH)
        GPIO.output(in2,GPIO.LOW)
        pwm1.ChangeDutyCycle(y)
        pwm0.ChangeDutyCycle(7.9)
    elif angle >= 110 and angle < 115:
        way = "RIGHT" 
        GPIO.output(in1,GPIO.HIGH)
        GPIO.output(in2,GPIO.LOW)
        pwm1.ChangeDutyCycle(y)
        pwm0.ChangeDutyCycle(8.2)
    elif angle >= 115 and angle <120:
        way = "RIGHT" 
        GPIO.output(in1,GPIO.HIGH)
        GPIO.output(in2,GPIO.LOW)
        pwm1.ChangeDutyCycle(y)
        pwm0.ChangeDutyCycle(8.5)
    elif angle >= 120 and angle <125:
        way = "RIGHT" 
        GPIO.output(in1,GPIO.HIGH)
        GPIO.output(in2,GPIO.LOW)
        pwm1.ChangeDutyCycle(y)
        pwm0.ChangeDutyCycle(8.8)
    elif angle >= 125 and angle <130:
        way = "RIGHT" 
        GPIO.output(in1,GPIO.HIGH)
        GPIO.output(in2,GPIO.LOW)
        pwm1.ChangeDutyCycle(y)
        pwm0.ChangeDutyCycle(9.1)
    elif angle >= 130:
        way = "RIGHT" 
        GPIO.output(in1,GPIO.HIGH)
        GPIO.output(in2,GPIO.LOW)
        pwm1.ChangeDutyCycle(y)
        pwm0.ChangeDutyCycle(9.4)
    else:
        way = "STRAIGHT" 
        GPIO.output(in1,GPIO.HIGH)
        GPIO.output(in2,GPIO.LOW)
        pwm1.ChangeDutyCycle(x)
        pwm0.ChangeDutyCycle(7)
    return way

def draw_head_line(frame, angle, line_color=(0, 0, 255), stickness=5 ):
    head_image = np.zeros_like(frame)
    height, width, _ = frame.shape

    # Note: the angle of:
    # 0-85 degree: turn left
    # 85-95 degree: going straight
    # 95-180 degree: turn right 
    angle_radian = angle / 180.0 * math.pi
    x1 = int(width / 2)
    y1 = height
    x2 = int(x1 - height / 2 / math.tan(angle_radian))
    y2 = int(height / 2)

    cv2.line(head_image, (x1, y1), (x2, y2), line_color, stickness)
    head_image = cv2.addWeighted(frame, 0.8, head_image, 1, 1)

    return head_image

def HCR(trig,echo):
    GPIO.output(trig, False)
    GPIO.output(trig, True)
    time.sleep(0.00001)
    GPIO.output(trig, False)

    while GPIO.input(echo)==0:
        pulse_start = time.time()

    while GPIO.input(echo)==1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start

    distance = pulse_duration * 17150
    distance = round(distance, 2)
    return distance
def stop(pwm1):
    pwm1.ChangeDutyCycle(0)
def end(pwm0,pwm1):
    pwm0.ChangeDutyCycle(0)
    pwm1.ChangeDutyCycle(0)

def main(pwm0,pwm1):
    in1,in2,echo,trig=3,4,20,21
    default_angle = 90
    cap = cv2.VideoCapture(0)

    while True:
        ret,frame = cap.read()
        
        edges = edges_detect(frame)

        ROIs = ROI(edges)

        line_coordinats = detect_line_coordinats(ROIs)

        lane_segments = avg_slope_intercept(frame, line_coordinats)

        steering_angle = calculate_angle(frame,lane_segments)

        stabilized_angle = stabilize_angle(7,default_angle,steering_angle,len(lane_segments))

        current_image = draw_head_line(frame, stabilized_angle)
        
        distance =HCR(trig,echo)
        
        if distance < 50:
            stop(pwm1)
        else:
            way = direction(stabilized_angle,in1,in2,pwm0,pwm1)
        

        print("YÖN-> " + way)
        print("Direksiyon Açısı: %s" % stabilized_angle)

        cv2.imshow("Goruntu",frame)
        cv2.imshow("Calisma Goruntusu",current_image)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            end(pwm0,pwm1)
            break

    cap.release()
    cv2.destroyAllWindows()
