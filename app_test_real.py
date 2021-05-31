from notification import *
from csicamera import *
from eyedetector import *
from mibandAPI import *
#from PIL import ImageFont, ImageDraw, Image
import numpy as np
import threading
import time
import cv2

screenState = 0

CSI = CSICamera(640, 480, 1280, 800, 30)
ED = EyeDetector('load_file')

miband = None


cv2.namedWindow("frame")

#Miband Connection
def loadingBand():
    global screenState, miband
    miband = mibandAPI("DB:28:14:20:F4:D0", "c2fa26313cba3df7cf0fe85f0e41dfe2")
    miband.initHeartRate()

    screenState = 281

t = threading.Thread(target=loadingBand)
t.start()


while True:
    drowloading = cv2.imread('images/loadingscreen.jpg')

    cv2.imshow('frame', drowloading)
    cv2.namedWindow('frame',cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty('frame', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    if screenState == 281:
        break

    if cv2.waitKey(1) == 27:
        break


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
currentHeartRate = 0 #심박수 정보
# defaultHeartRate = 0

f = open('hrate.txt', 'r')
deafaultHeartRate = (float(f.readline())*0.96)
f.close()

debugMode = True #디버그 모드를 사용할 것인가?

CSI.openCamera()
#CSI.openCameraUSB(0)

if  CSI.isCameraOpened() is False:
    print("카메라에 연결되어있지 않습니다.")
    exit()

#cv2.namedWindow("frame")
if ED.isModelNotLoaded():
    print("모델 데이터 로드에 실패하였습니다.")
    exit()

frame  = CSI.readFrame()

cv2.imshow('frame', frame)
cv2.namedWindow('frame',cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty('frame', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

def debugPrint(text):
    if debugMode == True:
        print(text)

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
            strIsEyes = "false"
            #눈 감긴 상태
            # strIsEyes = "false"
            # if alertLevel < 5:
            #     alertLevel += 1
            # AlertSound(alertLevel)
            totalClosedCount += 1
            debugPrint("Total Closed: " + str(totalClosedCount))
            
            
            if totalClosedCount >= 33:
                debugPrint("totalClosedCount is 10")
                debugPrint("totalClosedCount" + str(totalClosedCount) + "totalLaunchTime" + str(totalLaunchTime))
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
    debugPrint('time:' + str(timerLaunchTime))
    if timerLaunchTime >= 0.3:
        timerLaunchTime = 0
    timer.start()

def heartRateTimer():
    global currentHeartRate, alertLevel, totalClosedCount, totalLaunchTime, miband

    timerHR = threading.Timer(0.01, heartRateTimer)
    timerHR.name = "HeartRate_Timer"
    timerHR.daemon = True
    tmpHeartRate = 0
    try:
        tmpHeartRate = miband.loadHeartRate()
    except:
        miband.initHeartRate()
        tmpHeartRate = miband.loadHeartRate()
    if tmpHeartRate != 0:
        currentHeartRate = tmpHeartRate
        debugPrint(currentHeartRate)

        #4% 이상 깎이면 알림 증가
        if currentHeartRate < deafaultHeartRate:
            if alertLevel < 5:
                alertLevel += 1
                AlertSound(alertLevel)
            totalClosedCount = 0
            totalLaunchTime = 0


    timerHR.start()

detectTimer()
heartRateTimer()

prevTime = 0 #FPS 계산용
hrTime = time.time()

while True:
    frame = CSI.readFrame()
    if frame is None:
        break

    curTime = time.time()
    sec = curTime - prevTime
    prevTime = curTime
    fps = 1/(sec)

    if (time.time() - hrTime >= 12):
        miband.requestHeartRate()
        hrTime = time.time()

    labFPS = "FPS: %0.1f" % fps
    labFace = f"Face: {strIsFace}"
    labEyes = f"Eyes: {strIsEyes}"
    labHeartRate = f"HR: {currentHeartRate}"
    labAlertLevel = f"Level: {alertLevel}"

    cv2.putText(frame, labHeartRate, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (79, 79, 229), 2, cv2.LINE_AA)
    
    if debugMode == True:
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0))
        cv2.putText(frame, labFace, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, labEyes, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, labFPS, (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, labAlertLevel, (10, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1, cv2.LINE_AA)

    #한글 출력
    if alertLevel >= 1:
        stepimg = cv2.imread('step' + str(alertLevel) +'.jpg')
        frame = np.concatenate((frame, stepimg), axis=0)
    
    cv2.imshow('frame', frame)

    if cv2.waitKey(1) == 27: #ESC
        break

CSI.releaseCamera()
cv2.destroyAllWindows()
