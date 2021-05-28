import time
from notification import *
from csicamera import *
from eyedetector import *
import cv2
import threading
import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QMessageBox, QGraphicsOpacityEffect
from PyQt5.QtGui import QPixmap, QImage, qRgb
from PyQt5.QtCore import QCoreApplication, QObject





def numpyQImage(image):
    qImg = QImage()
    if image.dtype == np.uint8:
        if len(image.shape) == 2:
            channels = 1
            height, width = image.shape
            bytesPerLine = channels * width
            qImg = QImage(
                image.data, width, height, bytesPerLine, QImage.Format_Indexed8
            )
            qImg.setColorTable([qRgb(i, i, i) for i in range(256)])
        elif len(image.shape) == 3:
            if image.shape[2] == 3:
                height, width, channels = image.shape
                bytesPerLine = channels * width
                qImg = QImage(
                    image.data, width, height, bytesPerLine, QImage.Format_RGB888
                )
            elif image.shape[2] == 4:
                height, width, channels = image.shape
                bytesPerLine = channels * width
                fmt = QImage.Format_ARGB32
                qImg = QImage(
                    image.data, width, height, bytesPerLine, QImage.Format_ARGB32
                )
    return qImg

running = False







class App(QWidget):

    def __init__(self):
        super().__init__()
        self.setFixedSize(1280, 800)
        self.setWindowTitle('졸음운전 방지 시스템')

        # 변수 초기화
        self.fps = 0.
        self.strIsFace = "false"  # 얼굴 있는지 없는지
        self.strIsEyes = "false"  # 눈 있는지 없는지
        self.alertLevel = 0  # 경고 단계
        self.totalClosedCount = 0
        self.totalLaunchTime = 0
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0
        self.running = False
        self.func = None
        self.frame_loop_flag = True
        

        # GUI 그리는 부분
        self.initUI()


    def play(self):
        self.running = True
        self.func()
        print("Play!")

    def stop(self):
        self.running = False
        print("Stop!")
        self.x1 = 0
        self.x2 = 0
        self.y1 = 0
        self.y2 = 0

    def camera_release(self):
        self.frame_loop_flag = False
        
            

        
            

    

        

    def run(self):
        CSI = CSICamera(640, 480, 640, 480, 30)
        CSI.openCamera()

        ED = EyeDetector('load_file')

        if  CSI.isCameraOpened() is False:
            print("카메라에 연결되어있지 않습니다.") 
            exit()

        if ED.isModelNotLoaded():
            print("모델 데이터 로드에 실패하였습니다.")
            exit()

    

        frame  = CSI.readFrame() # 확인 필요!!!

        # 여기에 타이머 관련 코드 삽입
        def detectTimer():
            st = time.time()
            timer = threading.Timer(0.1, detectTimer)
            timer.name = "Detector_Timer"
            timer.daemon = True

            isFace, face_frame, self.x1, self.y1, self.x2, self.y2 = ED.CalculateFaceFrame(frame)


            if isFace is True:
                self.strIsFace = "true"
                if ED.DetectEyes(face_frame) is False:
                    #눈 감긴 상태
                    self.totalClosedCount += 1
                    print("Total Closed: " + str(self.totalClosedCount))

                    if self.totalClosedCount >= 150:
                        print("totalClosedCount is 10")
                        print("totalClosdCount" + str(self.totalClosedCount) + "totalLaunchTime" + str(self.totalLaunchTime))
                        if self.totalClosedCount / self.totalLaunchTime >= 0.15:
                            if self.alertLevel < 5:
                                self.alertLevel +=1
                            AlertSound(self.alertLevel)
                        else:
                            if self.alertLevel > 0:
                                self.alertLevel -= 1
                        self.totalClosedCount = 0
                        self.totalLaunchTime = 0

                else:
                    #눈을 뜬 상태
                    self.strIsEyes = "true"
                    if self.alertLevel > 0:
                        self.alertLevel -= 1

            else:
                self.strIsFace = "false"

            self.totalLaunchTime += 1
            et = time.time()
            timerLaunchTime = et - st
            print('time:', timerLaunchTime)
            if timerLaunchTime >= 0.3:
                timerLaunchTime = 0

            if self.running is False:
                return
            timer.start()



        prevTime = 0 #FPS 계산용
        self.func = detectTimer

        while self.frame_loop_flag:
            frame = CSI.readFrame()
            frame = cv2.resize(frame, dsize=(1280, 800), interpolation=cv2.INTER_LINEAR)
            if frame is None:
                QMessageBox.about(self, "Error", "Cannot read frame.") # 오류발생 수정 필요!
                print("cannot read frame.")
                break

            # FPS 측정
            curTime = time.time()
            sec = curTime - prevTime
            prevTime = curTime
            self.fps = 1/(sec)

            labFPS = "FPS: %0.1f" % self.fps
            labFace = f"Face: {self.strIsFace}"
            labEyes = f"Eyes: {self.strIsEyes}"

            # 프레임에 영상 정보 출력
            cv2.rectangle(frame, (self.x1, self.y1), (self.x2, self.y2), (0, 255, 0))
            cv2.putText(frame, labFPS, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1, cv2.LINE_AA)
            cv2.putText(frame, labFace, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1, cv2.LINE_AA)
            cv2.putText(frame, labEyes, (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1, cv2.LINE_AA)

            # 이미지 pixmap 객체로 변환
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, c = frame.shape
            qImg = QImage(frame.data, w, h, w*c, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qImg)
            self.video_display.setPixmap(pixmap)
        
        CSI.releaseCamera()
        

    def initUI(self):

        init_img = np.zeros((800, 1280), np.uint8)

        # 레이블 추가
        self.video_display = QLabel('', self)

        # 카메라 해제 버튼
        camera_release_Button = QPushButton('cap.release', self)
        camera_release_Button.move(1280, 800)
        camera_release_Button.setShortcut("q")

        # 윈도우 닫기 버튼
        close_Button = QPushButton('close', self)
        close_Button.move(1280,850)
        close_Button.setShortcut('ESC')

        # 화면 초기화
        init_img = numpyQImage(init_img)
        pixmap = QPixmap.fromImage(init_img)
        self.video_display.setPixmap(pixmap)

        # play 버튼
        play_Button = QPushButton('', self)
        play_Button.resize(400,400)
        play_Button.setStyleSheet("image:url(./start.png); border:0px;")
        play_Button.move(0,100)

        # stop 버튼
        stop_Button = QPushButton('', self)
        stop_Button.resize(400,400)
        stop_Button.setStyleSheet("image:url(./stop.png); border:0px;")
        stop_Button.move(800,100)

        # 버튼 기능 연결
        play_Button.clicked.connect(self.play)
        stop_Button.clicked.connect(self.stop)
        camera_release_Button.clicked.connect(self.camera_release)
        close_Button.clicked.connect(QCoreApplication.instance().quit)

        # 프레임 갱신 스레드 실행
        video_thread = threading.Thread(target=self.run)
        video_thread.daemon = True
        video_thread.start()

        self.show()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = App()
    sys.exit(app.exec_())

