import detect
import pwm
import manual
import cv2

print("WELCOME")
pwm0,pwm1,pwm2=pwm.main()
while True:
    try:
        selection = int(input("1-> Use Manual(Exit Q) 2-> Use automatic(Exit q) 3-> Exit"))
    except:
        pass
    if selection == 1:
        manual.main(pwm0,pwm1,pwm2)
    elif selection:
        detect.main(pwm0,pwm1)
    elif selection == 3:
        cv2.destroyAllWindows()
        break
    else:
        print("Make a valid choice, please.")
