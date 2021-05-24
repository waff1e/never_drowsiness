from notification import *
from csicamera import *
from eyedetector import *
import numpy as np
import threading
import time
import cv2

CSI = CSICamera(640, 480, 640, 480, 30)
ED = EyeDetector('load_file')

strIsFace = "false" #얼굴 있는지 없는지
strIsEyes = "false" #눈 있는지 없는지
alertLevel = 0 # 경고 단계
x1 = 0
y1 = 0
x2 = 0
y2 = 0
totalLaunchTime = 0 #10번 감을때까지 걸린 시간
totalClosedCount = 0 #눈 감은 횟수
timerLaunchTime = 0 #감지에 사용한 시간

CSI.openCamera()
#CSI.openCameraUSB(0)

if  CSI.isCameraOpened() is False:
    print("카메라에 연결되어있지 않습니다.")
    exit()

cv2.namedWindow("frame")
if ED.isModelNotLoaded():
    print("모델 데이터 로드에 실패하였습니다.")
    exit()

frame  = CSI.readFrame()

# 여기에 타이머 관련 코드 삽입
def detectTimer():
    global timerLaunchTime
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

    if isFace is True:
        strIsFace = "true"
        if ED.DetectEyes(face_frame) is False:
            #눈 감긴 상태
            # strIsEyes = "false"
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
    timer.start()

detectTimer()

prevTime = 0 #FPS 계산용

while True:
    frame = CSI.readFrame()
    if frame is None:
        break

    curTime = time.time()
    sec = curTime - prevTime
    prevTime = curTime
    fps = 1/(sec)

    labFPS = "FPS: %0.1f" % fps
    labFace = f"Face: {strIsFace}"
    labEyes = f"Eyes: {strIsEyes}"

    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0))
    cv2.putText(frame, labFPS, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1, cv2.LINE_AA)
    cv2.putText(frame, labFace, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1, cv2.LINE_AA)
    cv2.putText(frame, labEyes, (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1, cv2.LINE_AA)
    
    cv2.imshow('frame', frame)

    if cv2.waitKey(1) == 27: #ESC
        break

CSI.releaseCamera()
cv2.destroyAllWindows()
