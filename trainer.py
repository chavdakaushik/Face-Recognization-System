import os
import numpy as np
import cv2
from PIL import Image

cascadePath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath)

recognizer = cv2.face.LBPHFaceRecognizer_create()

path = "dataSet"

def getImagesWithId(path):
    imgpaths = [os.path.join(path, f) for f in os.listdir(path)]

    faces = []
    IDs = []

    for imgpath in imgpaths:
        faceImg = Image.open(imgpath).convert("L")
        faceNp = np.array(faceImg, 'uint8')
        ID = int(os.path.split(imgpath)[-1].split('.')[1])  # dataset//User.1.1.jpg
        faces.append(faceNp)
        IDs.append(ID)
        cv2.imshow("training", faceNp)
        cv2.waitKey(10)
    return IDs ,faces

Ids,faces  = getImagesWithId(path)
recognizer.train(faces, np.array(Ids))
recognizer.save("recognizer//trainingData.yml")
cv2.destroyAllWindows()