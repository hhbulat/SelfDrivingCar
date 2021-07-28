import cv2
import RPi.GPIO as GPIO
import time
import picamera


# Yönlendirme işlemleri.
def steering_car(select,duty0,duty1,pwm0,pwm1,in1,in2):
    if select==ord("w"):
        print("w")
        GPIO.output(in1,GPIO.HIGH)
        GPIO.output(in2,GPIO.LOW)
        pwm1.ChangeDutyCycle(duty1)
        duty1=duty1+3
        if duty1>=100:
            duty1=100
        
    elif select==ord("a"):
        print("a")
        pwm1.ChangeDutyCycle(duty1)
        pwm0.ChangeDutyCycle(duty0)
        duty0=duty0-0.3
        if duty0<=2:
            duty0=2

    elif select==ord("d"):
        print("d")
        pwm0.ChangeDutyCycle(duty0)
        duty0=duty0+0.3
        if duty0>=12:
            duty0=12
        
    elif select==ord("s"):
        print("s")
        GPIO.output(in1,GPIO.LOW)
        GPIO.output(in2,GPIO.HIGH)
        pwm1.ChangeDutyCycle(duty1)
        duty1=duty1+3
        if duty1<=0:
            duty1=0
    
    elif select==ord("q"):
        print("z")
        pwm1.ChangeDutyCycle(0)
        pwm0.ChangeDutyCycle(7)
        time.sleep(1)
        pwm0.stop()
        pwm1.stop()
    elif select==ord("r"):
        duty0=7
        duty1=0
        pwm0.ChangeDutyCycle(duty0)
        pwm0.ChangeDutyCycle(duty1)
    else:
        duty1=duty1-0.5
        if duty1<=10:
            duty1=10
    return duty0,duty1
# Kamera Yönlendirme işlemleri
def steering_camera(select,duty2,pwm2):
    if select == ord("1"):
        if duty2!=7.8:
            duty2=7.8
            pwm2.ChangeDutyCycle(duty2)
    elif select == ord("2"):
        if duty2!=0:
            duty2=0
            pwm2.ChangeDutyCycle(duty2)
    elif select == ord("3"):
        if duty2!=6.2:
            duty2=6.2
            pwm2.ChangeDutyCycle(duty2)

def control(duty0,duty1):
    if duty0 >= 12:
        duty0 = 12
    elif duty0 <= 2:
        duty0 = 2
    if duty1 >= 100:
        duty0 = 100
    elif duty1 <= 20:
        duty0 = 20
def main(pwm0,pwm1,pwm2):
    in1,in2=3,4
    duty0=7
    duty1=30
    duty2=7
    print("W-> İleri S-> Geri A->Sol D-> Sağ 1-> E-> Hareketi Durdur 1->Kamera Saat Yönünde 3-> Kamera Saat yönünün Tersinde 2-> Kamera dönmesini durdur")
    print("Z-> Çıkış")
    cap = cv2.VideoCapture(0)
    while True:
        ret,frame = cap.read()
        cv2.imshow("IMAGE",frame)
        select = cv2.waitKey(1)
        control(duty0,duty1)
        duty0,duty1=steering_car(select,duty0,duty1,pwm0,pwm1,in1,in2)
        steering_camera(select,duty2,pwm2)
        if select & 0xFF == ord("q"):
            pwm0.ChangeDutyCycle(0)
            pwm1.ChangeDutyCycle(0)
            cap.release()
            cv2.destroyAllWindows()
            break
    