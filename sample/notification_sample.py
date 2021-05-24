from notification import *
import threading
import cv2

alertLevel = 0

def detectTimer():
    timer = threading.Timer(1, detectTimer)
    timer.name = "Detector_Timer"
    timer.daemon = True

    global alertLevel
    
    if alertLevel < 5:
        alertLevel += 1
        alert_level(alertLevel)

    timer.start()

detectTimer()

while(True):
    if cv2.waitKey(1) == 27: #ESC
        break
