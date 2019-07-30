import cv2
import numpy as np
import mysql.connector

faceDetect = cv2.CascadeClassifier("haarcascade_frontalface_default.xml");
cam = cv2.VideoCapture(0)
cam.set(3,1920)
cam.set(4,1080)

rec =  cv2.face.LBPHFaceRecognizer_create()

rec.read("recognizer//trainingData.yml")

font =cv2.FONT_HERSHEY_COMPLEX_SMALL

path = "dataset"

def getProfile(id):
    conn = mysql.connector.connect(
        host = 'localhost',
        user = 'root',
        password = 'root',
        database = 'FaceBase'
    )

    query = "select * from People where id="+str(id)
    mycursor = conn.cursor()
    mycursor.execute(query)
    result = mycursor.fetchall()
    profile = None

    for row in result:
        profile = row
    conn.close()
    return profile

while(True):
    ret, frame = cam.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceDetect.detectMultiScale(gray, 1.2, 5);

    for (x, y, w, h) in faces:
        
        # cv2.rectangle(frame, (x , y), (x + w, y + h), (0, 255, 0), 2)
        # cv2.waitKey(100);


        cv2.rectangle(frame,(x,y),(x+w,y+h),(225,0,0),2)
        
        id,conf  = rec.predict(gray[y:y+h,x:x+w])
        
        profile = getProfile(id)         
        
        if (profile != None):
            if(conf <50):
                cv2.putText(frame, str(profile[1]), (x, y + h), font, 1, (230, 0, 0), 2);
            else:
                cv2.putText(frame, str('unknown'), (x, y + h), font, 1, (230, 0, 0), 2);
              
    cv2.imshow("Face", frame);
     
    if (cv2.waitKey(1)==ord('q')):
        break;

cam.realese()
cv2.destroyAllWindows()

            