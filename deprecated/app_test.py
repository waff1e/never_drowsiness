from notification import *
from csicamera import *
from eyedetector import *
from mibandAPI import *
import numpy as np
import threading
import time
import cv2
import asyncio

CSI = CSICamera(640, 480, 1280, 800, 30)
ED = EyeDetector('load_file')

# MiBand Connection
#miband = mibandAPI("DB:28:14:20:F4:D0", "c2fa26313cba3df7cf0fe85f0e41dfe2")
#miband.initHeartRate()

strIsFace = "false" #얼굴 있는지 없는지
strIsEyes = "false" #눈 있는지 없는지  
alertLevel = 0 # 경고 단계
x1 = 0
y1 = 0
x2 = 0
y2 = 0
totalLaunchTime = 0 #10번 감을때까지 걸린 시간
totalClosedCount = 0 #눈 감은 횟수
timerLaunchTime = 0 #눈 감기에 사용한 시간
currentHeartRate = 0 #심박수 정보

runState = False #졸음운전 감지가 진행되고 있는가?

#Button Coordinate [y1, y2, x1, x2]
#Text Location(Left Upper): x = 30 y = y1 +30
drowsinessButton = [140, 180, 10, 180]

#Button Color
btnColorRed = (2, 2, 229)
btnColorGreen = (62, 186, 1)

#Drowsiness Button State
dBColor = btnColorRed
dBText = "STOPPED"

CSI.openCamera()
#CSI.openCameraUSB(0)

if  CSI.isCameraOpened() is False:
    print("카메라에 연결되어있지 않습니다.")
    exit()

def clickEvents(event, x, y,flags, params):
    # check if the click is within the dimensions of the button
    if event == cv2.EVENT_LBUTTONDOWN:
        if y > drowsinessButton[0] and y < drowsinessButton[1] and x > drowsinessButton[2] and x < drowsinessButton[3]:   
            global dBText, dBColor, runState
            if runState == False:
                runState = True
                dBColor = btnColorGreen
                dBText = "RUNNING"
                detectTimer()
            else:
                runState = False
                dBColor = btnColorRed
                dBText = "STOPPED"

#cv2.namedWindow("frame", cv2.WND_PROP_FULLSCREEN)
#cv2.createButton("Back", back, None, cv2.QT_PUSH_BUTTON, 1)

if ED.isModelNotLoaded():
    print("모델 데이터 로드에 실패하였습니다.")
    exit()

frame  = CSI.readFrame()

cv2.imshow('frame', frame)
cv2.namedWindow('frame',cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty('frame', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
cv2.setMouseCallback('frame', clickEvents)
#cv2.createButton("Back", back, None, cv2.QT_PUSH_BUTTON, 1)

# 여기에 타이머 관련 코드 삽입
def detectTimer():
    global timerLaunchTime
    global frame
    st = time.time()
    timer = threading.Timer(0.3 - timerLaunchTime, detectTimer)
    timer.name = "Detector_Timer"
    timer.daemon = True

    global x1, y1, x2, y2
    isFace, face_frame, x1, y1, x2, y2 = ED.CalculateFaceFrame(frame)

    global strIsFace
    global strIsEyes
    global alertLevel
    global totalClosedCount
    global totalLaunchTime
    global runState

    if isFace is True:
        strIsFace = "true"
        if ED.DetectEyes(face_frame) is False:
            #눈 감긴 상태
            strIsEyes = "false"
            # if alertLevel < 5:
            #     alertLevel += 1
            # AlertSound(alertLevel)
            totalClosedCount += 1
            print("Total Closed: " + str(totalClosedCount))
            
            
            if totalClosedCount >= 33:
                print("totalClosedCount is 10")
                print("totalClosedCount" + str(totalClosedCount) + "totalLaunchTime" + str(totalLaunchTime))
                if totalClosedCount / totalLaunchTime >= 0.15:
                    if alertLevel < 5:
                        alertLevel += 1
                    AlertSound(alertLevel)
                else:
                    if alertLevel > 0:
                        alertLevel -= 1
                totalClosedCount = 0
                totalLaunchTime = 0
            
        else:
            #눈을 뜬 상태
            strIsEyes = "true"
            # if alertLevel > 0:
            #     alertLevel -= 1

    else:
        strIsFace = "false"
    
    totalLaunchTime += 1
    et =time.time()
    timerLaunchTime = et - st

    print('time:', timerLaunchTime)
    if timerLaunchTime >= 0.3:
        timerLaunchTime = 0
    
    if runState == True:
        timer.start()
    else:
        timerLaunchTime = 0
        totalClosedCount = 0
        alertLevel = 0

# def heartRateTimer():
#     global currentHeartRate
# #     t = time.time()
#     timerHR = threading.Timer(0.01, heartRateTimer)
#     timerHR.name = "HeartRate_Timer"
#     timerHR.daemon = True
#     tmpHeartRate = 0
#     try:
#         tmpHeartRate = miband.loadHeartRate()
#     except:
#         miband.initHeartRate()
#         tmpHeartRate = miband.loadHeartRate()
#     if tmpHeartRate != 0:
#         currentHeartRate = tmpHeartRate
#         print(currentHeartRate)

# #     if (time.time() - t >= 12):
# #         miband.requestHeartRate()
# #         t = time.time()
#     print("HEARTRATETHREAD ")
#     if runState == True:
#         timerHR.start()

if runState == True:
    detectTimer()
#    heartRateTimer()

prevTime = 0 #FPS 계산용

hrTime = time.time()

def main():
    global CSI, strIsFace, strIsEyes, x1, y1, x2, y2, drowsinessButton, btnColorGreen, dBColor, dBText, prevTime, hrTime

    #future = asyncio.ensure_future(miband.get_realtime())

    while True:
        frame = CSI.readFrame()
        if frame is None:
            break

        curTime = time.time()
        sec = curTime - prevTime
        prevTime = curTime
        fps = 1/(sec)

        if (time.time() - hrTime >= 12):
            #miband.requestHeartRate()
            hrTime = time.time()

        labFPS = "FPS: %0.1f" % fps
        labFace = f"Face: {strIsFace}"
        labEyes = f"Eyes: {strIsEyes}"
        labHeartRate = f"HR: {currentHeartRate}"

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0))
        cv2.putText(frame, labFPS, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, labFace, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, labEyes, (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, labHeartRate, (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1, cv2.LINE_AA)
        frame[drowsinessButton[0]:drowsinessButton[1],drowsinessButton[2]:drowsinessButton[3]] = dBColor
        cv2.putText(frame, dBText ,(30,170),cv2.FONT_HERSHEY_PLAIN, 2,(255, 255, 255),3)
        
        cv2.imshow('frame', frame)
        # cv2.namedWindow('frame',cv2.WND_PROP_FULLSCREEN)
        #cv2.setWindowProperty('frame', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        if cv2.waitKey(1) == 27: #ESC
            break

main()

CSI.releaseCamera()
cv2.destroyAllWindows() 