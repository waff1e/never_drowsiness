import cv2

class CSICamera:

    def __init__(self, width, height, display_width, display_height, framerate):
        self._width = width
        self._height = height
        self._display_width = display_width
        self._display_height = display_height
        self._framerate = framerate
        
    
    def CreateGStreamer(self):
        return (
            "nvarguscamerasrc ! "
            "video/x-raw(memory:NVMM), "
            f"width=(int){self._width}, height=(int){self._height}, "
            f"format=(string)NV12, framerate=(fraction){self._framerate}/1 ! "
            f"nvvidconv flip-method=0 ! "
            f"video/x-raw, width=(int){self._display_width}, height=(int){self._display_height}, format=(string)GRAY8 ! "
            f"videoconvert ! "
            f"video/x-raw, format=(string)BGR ! appsink"
        )

    def openCamera(self):
        self.cam = cv2.VideoCapture(self.CreateGStreamer(), cv2.CAP_GSTREAMER)
        
    def openCameraUSB(self, num):
        self.cam = cv2.videoCapture(num)

    def isCameraOpened(self):
        return self.cam.isOpened()

    def readFrame(self):
        _, frame = self.cam.read()
        return frame

    def releaseCamera(self):
        self.cam.release()