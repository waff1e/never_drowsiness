from mibandAPI import *
import numpy as np
import time
import cv2
import os
level = 0

cv2.namedWindow("img")

def clickEvents(event, x, y,flags, params):
    # check if the click is within the dimensions of the button
    global level
    if event == cv2.EVENT_LBUTTONDOWN:
        if level == 0:   
            level = 1
            print("ggggg")
        
        if level == 194:
            level = 725


while True:
    print("HHH")
    img = cv2.imread('hrstart.jpg')

    cv2.imshow('img', img)
    cv2.setWindowProperty('img', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setMouseCallback('img', clickEvents)

    if level == 1:
        break

    if cv2.waitKey(1) == 27: #ESC
        break

#cv2.setWindowProperty('img', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

level = 194

miband = mibandAPI("DB:28:14:20:F4:D0", "c2fa26313cba3df7cf0fe85f0e41dfe2")
miband.initHeartRate()

i = 0
currentHeartRate = 0
hrArr = []
result = 0

hrTime = time.time()

while True:
    #cv2.imshow('img', img)
    #cv2.setWindowProperty('img', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    #cv2.setMouseCallback('img', clickEvents)

    tmpHeartRate = miband.loadHeartRate()
    if tmpHeartRate != 0:
        currentHeartRate = tmpHeartRate
        print(currentHeartRate)
        hrArr.append(currentHeartRate)
        i += 1

    if (time.time() - hrTime >= 12):
        miband.requestHeartRate()
        hrTime = time.time()

    img = cv2.imread('hrbackgrnd.jpg')
    cv2.putText(img, str(currentHeartRate), (10, 600), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1, cv2.LINE_AA)
    cv2.imshow('img', img)
    cv2.setWindowProperty('img', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    

    if i == 3:
        break;

result = sum(hrArr) / len(hrArr)

with open('hrate.txt', 'w') as f:
    f.write(str(result))

print(str(result))
print("측정완료")

while True:
    img = cv2.imread('hrbackgrnd2.jpg')
    cv2.imshow('img', img)

    if cv2.waitKey(1) == 27: #ESC
        break

    if level == 725:
        break

cv2.destroyAllWindows()

os.system('python3 app_test_real.py')
