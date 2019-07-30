import cv2
import numpy as np
import mysql.connector

faceDetect = cv2.CascadeClassifier("haarcascade_frontalface_default.xml");
cam = cv2.VideoCapture(0)

cam.set(3,1080)
cam.set(4,720)

def insert(Id, Name):
    conn = mysql.connector.connect(
        host = 'localhost',
        user = 'root',
        password = 'root',
        database = 'FaceBase'
    )

    query = "select * from People where id="+str(Id)
    mycursor = conn.cursor()
    mycursor.execute(query)
    result = mycursor.fetchall()

    isRecoredExist = 0

    for row in result:
        isRecoredExist = 1
    if(isRecoredExist == 1):
        query = "update People set name = "+str(Name)+"where id = "+str(Id)
    else:
        query = "insert into People values("+str(Id)+","+str(Name)+")"

    mycursor.execute(query)
    conn.commit()
    conn.close()


id = input("Enter User id :-")
name = input("Enter Name :- ")

insert(id,name)

imageNum = 0

while(True):
    ret, img = cam.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceDetect.detectMultiScale(gray, 1.4, 5);

    for (x, y, w, h) in faces:
        imageNum += 1
        cv2.imwrite("dataSet/User." + str(id) + "."+ str(imageNum) + ".jpg", gray[y: y + h, x: x + w])
        cv2.rectangle(img, (x , y), (x + w, y + h), (0, 255, 0), 2)
        cv2.waitKey(100);

    cv2.imshow("Face", img);
    cv2.waitKey(1)
 
    if (imageNum > 30):
        cam.realese()

        cv2.destroyAllWindows()
        break;

    