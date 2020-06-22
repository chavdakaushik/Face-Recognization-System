import tkinter as tk
from tkinter import Text
import tkinter.font as font
import cv2
import mysql.connector
import os
import numpy as np
from PIL import Image

window = tk.Tk()

window.geometry('1280x720')
# window.configure(background='cyan')

window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)

message = tk.Label(window, text="Enter Details" ,width=30  ,height=3,font=('times', 30, ' bold ')) 
message.place(x=400, y=20)

lbl = tk.Label(window, text="Enter ID",width=20  ,height=2  ,font=('times', 15, ' bold ') ) 
lbl.place(x=300, y=200)

txt = tk.Entry(window,width=20 ,font=('times', 15, ' bold '))
txt.place(x=600, y=215)

lbl2 = tk.Label(window, text="Enter Name",width=20  ,height=2 ,font=('times', 15, ' bold ')) 
lbl2.place(x=300, y=300)

txt2 = tk.Entry(window,width=20 ,font=('times', 15, ' bold ')  )
txt2.place(x=600, y=315)

def clear():
    txt.delete(0, 'end')    

def clear2():
    txt2.delete(0, 'end')        

def takeImages():
	faceDetect = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
	url = 'http://172.16.2.234:8080/video'
	cam = cv2.VideoCapture(url)

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
	        query = "insert into People(id, name) values("+Id+","+Name+")"

	    mycursor.execute(query)
	    conn.commit()
	    conn.close()

	id = txt.get()
	name = txt2.get()

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
	 
	    if (imageNum > 10):
	        cv2.destroyAllWindows()
	        break;

def trainImages():
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
	        # cv2.imshow("training", )
	        cv2.waitKey(10)
	    return IDs ,faces

	Ids,faces  = getImagesWithId(path)
	recognizer.train(faces, np.array(Ids))
	recognizer.save("recognizer//trainingData.yml")
	cv2.destroyAllWindows()

def trackImages():
	trainImages()
	faceDetect = cv2.CascadeClassifier("haarcascade_frontalface_default.xml");
	url = 'http://172.16.2.234:8080/video'
	cam = cv2.VideoCapture(url)
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
	    faces = faceDetect.detectMultiScale(gray, 1.2, 5, flags=cv2.CASCADE_SCALE_IMAGE);

	    for (x, y, w, h) in faces:
	        
	        cv2.rectangle(frame,(x,y),(x+w,y+h),(225,0,0),2)
	        
	        id,conf  = rec.predict(gray[y:y+h,x:x+w])
	        
	        profile = getProfile(id)         
	        
	        if (profile != None):
	            if(conf < 100):
	                # cv2.putText(frame, (str(profile[1]), conf), (x - 10, y - 10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0));
	                cv2.putText(frame, '%s - %.0f' % (str(profile[1]), 100-conf), (x-10, y-10), cv2.FONT_HERSHEY_PLAIN,1,(0, 255, 0))
	            else:
	                cv2.putText(frame, str('unknown'), (x - 10, y - 10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0));
	              
	    cv2.imshow("Face", frame);
	     
	    if (cv2.waitKey(1)==ord('q')):
	        break;

	cv2.destroyAllWindows()

def startUp():
	faceDetect = cv2.CascadeClassifier("haarcascade_frontalface_default.xml");
	url = 'http://172.16.2.234:8080/video'
	cam = cv2.VideoCapture(url)
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
	        
	        cv2.rectangle(frame,(x,y),(x+w,y+h),(225,0,0),2)
	        
	        id,conf  = rec.predict(gray[y:y+h,x:x+w])
	        
	        profile = getProfile(id)
	        
	        if (profile != None):
	        	if(str(profile[1]) == str("Kaushik")):
	        		if (conf < 50):
	        			del(cam)
	        			cv2.destroyAllWindows()
	        			window.mainloop()
	    cv2.imshow("Face", frame)
	     
	    if (cv2.waitKey(1)==ord('q')):
	        break;

	cv2.destroyAllWindows()

clearButton = tk.Button(window, text="Clear", command=clear  ,width=10  ,height=1 ,font=('times', 15, ' bold '))
clearButton.place(x=950, y=200)

clearButton2 = tk.Button(window, text="Clear", command=clear2 ,width=10  ,height=1,font=('times', 15, ' bold '))
clearButton2.place(x=950, y=300)    

takeImg = tk.Button(window, text="Take Images", command=takeImages ,width=20  ,height=1 ,font=('times', 15, ' bold '))
takeImg.place(x=300, y=500)

trackImg = tk.Button(window, text="Track Images", command=trackImages  ,width=20  ,height=1 ,font=('times', 15, ' bold '))
trackImg.place(x=600, y=500)

quitWindow = tk.Button(window, text="Quit", command=window.destroy   ,width=20  ,height=1 ,font=('times', 15, ' bold '))
quitWindow.place(x=900, y=500)
 
window.mainloop()
# startUp()