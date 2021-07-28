import RPi.GPIO as GPIO

def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # Used Rpi GPIO's output
    ena,in1,in2,servo,camservo,echo,trig=2,3,4,17,5,20,21
    GPIO.setup(ena,GPIO.OUT)
    GPIO.setup(in1,GPIO.OUT)
    GPIO.setup(in2,GPIO.OUT)
    GPIO.setup(servo,GPIO.OUT)
    GPIO.setup(camservo,GPIO.OUT)
    GPIO.setup(trig,GPIO.OUT)
    GPIO.setup(echo,GPIO.IN)

    # PWM Setup
    pwm0=GPIO.PWM(servo,50)
    pwm1=GPIO.PWM(ena,100)
    pwm2= GPIO.PWM(camservo,50)

    pwm0.start(0)
    pwm1.start(0)
    pwm2.start(0)
    return pwm0,pwm1,pwm2