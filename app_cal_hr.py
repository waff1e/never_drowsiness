from mibandAPI import *
import numpy as np
import time
import threading
import cv2
import os

miband = None
level = 0

cv2.namedWindow("img")

def clickEvents(event, x, y,flags, params):
    # check if the click is within the dimensions of the button
    global level
    if event == cv2.EVENT_LBUTTONDOWN:
        if level == 0:   
            level = 1

        
        if level == 194:
            level = 725


while True:

    img = cv2.imread('images/hrbackground.jpg')

    cv2.imshow('img', img)
    cv2.setWindowProperty('img', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setMouseCallback('img', clickEvents)

    if level == 1:
        break

    if cv2.waitKey(1) == 27: #ESC
        break

i = 0
currentHeartRate = 0
hrArr = []
result = 0

hrTime = time.time()

def loadingScreen():
    global i, currentHeartRate, hrArr, result, level, hrTime
    global miband

    miband = mibandAPI("DB:28:14:20:F4:D0", "c2fa26313cba3df7cf0fe85f0e41dfe2")
    miband.initHeartRate()

    while True:

        tmpHeartRate = miband.loadHeartRate()
        if tmpHeartRate != 0:
            currentHeartRate = tmpHeartRate
            print("Realtime Heart BPM: " + str(currentHeartRate))
            hrArr.append(currentHeartRate)
            i += 1

        if (time.time() - hrTime >= 12):
            miband.requestHeartRate()
            hrTime = time.time()
        

        if i == 3:
            break

    result = sum(hrArr) / len(hrArr)

    with open('hrate.txt', 'w') as f:
        #f.write(str(result))
        f.write("40")

    level = 194

    print("Average HeartRate: " + str(result))

        
t = threading.Thread(target=loadingScreen)
t.start()

while True:
    img = cv2.imread('images/hrcalculate.jpg')

    cv2.putText(img, "HR: " + str(currentHeartRate), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (79, 79, 229), 2, cv2.LINE_AA)
    cv2.imshow('img', img)

    cv2.setWindowProperty('img', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setMouseCallback('img', clickEvents)
    if level == 194:
        break

    if cv2.waitKey(1) == 27:
        break

while True:
    img = cv2.imread('images/hrbackground2.jpg')
    cv2.imshow('img', img)

    if cv2.waitKey(1) == 27: #ESC
        break

    if level == 725:
        break

miband.disconnect()

cv2.destroyAllWindows()

os.system('python3 app_test_real.py')
