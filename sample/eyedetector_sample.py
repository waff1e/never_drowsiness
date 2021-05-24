from csicamera import *
from eyedetector import *
import cv2
ed = EyeDetector('load_file')
csi = CSICamera(640, 480, 640, 480, 30)
csi.openCamera()
cv2.namedWindow('frame')
while(True):
    _, frame = csi.readFrame()
    (isFace, face_frame, x1, y1, x2, y2) = ed.CalculateFaceFrame(frame)
    if isFace is False:
        print("얼굴 없어")
    else:
        print("얼굴 있어")
    cv2.imshow('frame', frame)
    
    if cv2.waitKey(1) == 27:
        break


cap.release()
cv2.destroyAllWindows()
