import cv2

class EyeDetector:
    def __init__(self, dir_model):
        self.eye_cascPath = f"{dir_model}/haarcascade_eye_tree_eyeglasses.xml"
        self.model = f"{dir_model}/res10_300x300_ssd_iter_140000.caffemodel"
        self.config = f"{dir_model}/deploy.prototxt"
        self.eyeCascade = cv2.CascadeClassifier(self.eye_cascPath)
        self.net = cv2.dnn.readNet(self.model, self.config)

    def CalculateFaceFrame(self, frame):
        blob = cv2.dnn.blobFromImage(frame, 1, (300, 300), (104, 177, 123))
        self.net.setInput(blob)
        detect = self.net.forward()
        detect = detect[0, 0, :, :]
        (h, w) = frame.shape[:2]

        for i in range(detect.shape[0]):
            confidence = detect[i, 2]
            if confidence < 0.5:
                break
            else:

                x1 = int(detect[i, 3] * w)
                y1 = int(detect[i, 4] * h)
                x2 = int(detect[i, 5] * w)
                y2 = int(detect[i, 6] * h)

                face_frame = frame[y1:y2, x1:x2]
                return True, face_frame, x1, y1, x2, y2

        return False, None, 0, 0, 0, 0

    def DetectEyes(self, frame):
        eyes = self.eyeCascade.detectMultiScale(
        frame,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        )
        if len(eyes) == 0:
           return False #CLOSE
        else:
            return True #OPEN

    def isModelNotLoaded(self):
        return self.net.empty()