import time
from notification import *
from csicamera import *
from eyedetector import *
import cv2
import threading
import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QMessageBox
from PyQt5.QtGui import QPixmap, QImage, qRgb

running = False

class App(QWidget):

    def __init__(self):
        super().__init__()

        # CSI.openCameraUSB(0)

        self.fps = 0.
        self.strIsFace = "false"  # 얼굴 있는지 없는지
        self.strIsEyes = "false"  # 눈 있는지 없는지

        self.alertLevel = 0  # 경고 단계
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0
        self.running = False
        self.func = None

        self.initUI()

    def numpyQImage(self,image):
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



    def play(self):
        self.running = True
        self.func()

        # th = threading.Thread(target=self.run)
        # th.daemon = True
        # th.start()
        print("Play!")

    def stop(self):
        self.running = False
        # time.sleep(0.3)
        print("Stop!")
        self.x1 = 0
        self.x2 = 0
        self.y1 = 0
        self.y2 = 0
        

    def run(self):
        CSI = CSICamera(640, 480, 640, 480, 30)
        CSI.openCameraUSB(0)

        width = CSI.getWidth()
        height = CSI.getHeight()

        

        self.video_display.resize(int(width), int(height))

        ED = EyeDetector('load_file')



        if  CSI.isCameraOpened() is False:
            print("카메라에 연결되어있지 않습니다.") 
            exit()
        #cv2.namedWindow("frame") # GUI 창이 하나 더 생겨서 주석 처리 함
        if ED.isModelNotLoaded():
            print("모델 데이터 로드에 실패하였습니다.")
            exit()

        frame  = CSI.readFrame()
        # frame = cv2.resize(frame, dsize=(640, 480), interpolation=cv2.INTER_LINEAR)

# 여기에 타이머 관련 코드 삽입
        def detectTimer():
            timer = threading.Timer(1, detectTimer)
            timer.name = "Detector_Timer"
            timer.daemon = True

            isFace, face_frame, self.x1, self.y1, self.x2, self.y2 = ED.CalculateFaceFrame(frame)


            if isFace is True:
                self.strIsFace = "true"
                if ED.DetectEyes(face_frame) is False:
                    #눈 감긴 상태
                    self.strIsEyes = "false"
                    if self.alertLevel < 5:
                        self.alertLevel += 1
                    AlertSound(self.alertLevel)
                else:
                    #눈을 뜬 상태
                    self.strIsEyes = "true"
                    if self.alertLevel > 0:
                        self.alertLevel -= 1

            else:
                self.strIsFace = "false"
            if self.running is False:
                return
            timer.start()

        # def checkisTrue():
        #     check_timer = threading.Timer(1, checkisTrue)
        #     check_timer.name = "Check_Timer"
        #     check_timer.daemon = True

        #     if self.running is True: # Play버튼 클릭 이벤트가 발생하면 s@@@@Play 버튼 이벤트 처리 후 지울 것
        #        self.True

        #     else:

            


        prevTime = 0 #FPS 계산용
        self.func = detectTimer

        while True:
            frame = CSI.readFrame()
            frame = cv2.resize(frame, dsize=(640, 480), interpolation=cv2.INTER_LINEAR)
            if frame is None:
                QMessageBox.about(self, "Error", "Cannot read frame.") # 오류발생 수정 필요!
                print("cannot read frame.")
                break

            curTime = time.time()
            sec = curTime - prevTime
            prevTime = curTime
            self.fps = 1/(sec)

            labFPS = "FPS: %0.1f" % self.fps
            labFace = f"Face: {self.strIsFace}"
            labEyes = f"Eyes: {self.strIsEyes}"

            cv2.rectangle(frame, (self.x1, self.y1), (self.x2, self.y2), (0, 255, 0))
            print(self.x1, self.x2, self.y1, self.y2)
            cv2.putText(frame, labFPS, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1, cv2.LINE_AA)
            cv2.putText(frame, labFace, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1, cv2.LINE_AA)
            cv2.putText(frame, labEyes, (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1, cv2.LINE_AA)


            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, c = frame.shape
            qImg = QImage(frame.data, w, h, w*c, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qImg)
            self.video_display.setPixmap(pixmap)



        CSI.releaseCamera()
        cv2.destroyAllWindows()

#        while running:
#            img = CSI.readFrame()
#
##            if ret:
#            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#            h, w, c = img.shape
#            qImg = QImage(img.data, w, h, w*c, QImage.Format_RGB888)
#            pixmap = QPixmap.fromImage(qImg)
#            self.label.setPixmap(pixmap)
#
##            else:
##                QMessageBox.about(self, "Error", "Cannot read frame.") # 오류발생 수정 필요!
##                
##                print("cannot read frame.")
##                break
#        cap.release()
#        print("Thread end.")

    def initUI(self):

        img = np.zeros((480,640), np.uint8)

        # 버튼 추가
        play_Button = QPushButton('play')
        stop_Button = QPushButton('stop')

        # 레이블 추가
        self.video_display = QLabel()
        self.framerate_label = QLabel(f'FPS:{self.fps}', self)
        self.face_check_label = QLabel(f'얼굴인식:{self.strIsFace}', self)
        self.eye_check_label = QLabel(f'눈인식:{self.strIsEyes}', self)

        # 화면 초기화
        sample = self.numpyQImage(img)
        pixmap = QPixmap.fromImage(sample)
        self.video_display.setPixmap(pixmap)

        # 레이아웃 설정
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.video_display)
        hbox.addWidget(play_Button)
        hbox.addWidget(stop_Button)
        hbox.addStretch(1)

        vbox = QVBoxLayout()

        vbox.addStretch(1)
        vbox.addWidget(self.framerate_label)
        vbox.addWidget(self.face_check_label)
        vbox.addWidget(self.eye_check_label)
        vbox.addStretch(3)
        vbox.addLayout(hbox)
        vbox.addStretch(1)

        self.setLayout(vbox)
        self.setWindowTitle('졸음운전 방지 시스템')
        self.setGeometry(0, 0, 500, 500)
        self.video_display.resize(500, 500)

        th = threading.Thread(target=self.run)
        th.daemon = True
        th.start()
        self.show()

        play_Button.clicked.connect(self.play)
        stop_Button.clicked.connect(self.stop)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = App()
    sys.exit(app.exec_())

