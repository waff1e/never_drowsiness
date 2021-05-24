from csicamera import *
import cv2

csi = CSICamera(640, 480, 640, 480, 30)
csi.openCamera()
cv2.namedWindow('frame')
while(True):
    frame = csi.readFrame()
    cv2.imshow('frame', frame)
    
    if cv2.waitKey(1) == 27:
        break


cap.release()
cv2.destroyAllWindows()
