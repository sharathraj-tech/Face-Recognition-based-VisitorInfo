import os
import shutil
import cv2
import numpy as np
from PIL import Image, ImageTk
import pandas as pd
import datetime
import time
import sqlite3
from datetime import datetime
import pickle
import PySimpleGUI as sg

def TakeImages(uid):
    Id = str(uid)
    if not os.path.exists('VisitorImages/' + Id):
        os.makedirs('VisitorImages/' + Id)
    else:
        return "ERRORFOLDER"
    cam = cv2.VideoCapture(0)
    harcascadePath = "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(harcascadePath)
    sampleNum = 0
    while True:
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            # incrementing sample number
            sampleNum = sampleNum + 1
            # saving the captured face in the dataset folder TrainingImage
            cv2.imwrite('VisitorImages/' + Id + '/' + str(sampleNum) + '.jpg', gray[y:y + h, x:x + w])
            # display the frame
            cv2.imshow('CAPTURE IMAGES', img)
        # wait for 100 miliseconds
        if cv2.waitKey(100) & 0xFF == ord('q'):
            break
        # break if the sample number is more than 100
        elif sampleNum > 60:
            break
    cam.release()
    cv2.destroyAllWindows()
    return "SUCCESS"


def TrainImages():
    recognizer = cv2.face_LBPHFaceRecognizer.create()  # recognizer = cv2.face.LBPHFaceRecognizer_create()#$cv2.createLBPHFaceRecognizer()
    harcascadePath = "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(harcascadePath)
    faces, Id = getImagesAndLabels("VisitorImages")
    recognizer.train(faces, np.array(Id))
    recognizer.save("Trainer\Trainer.yml")
    res = "Image Trained"  # +",".join(str(f) for f in Id)
    # message.configure(text= res)


def getImagesAndLabels(path):
    # get the path of all the files in the folder
    # create empty face list
    faces = []
    # create empty ID list
    Ids = []
    current_id = 0
    label_ids = {}
    y_label = []
    x_train = []

    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith("png") or file.endswith("jpg"):
                path = os.path.join(root, file)
                label = os.path.basename(root).replace("", "").upper()
                print(label, path)
                if label in label_ids:
                    pass
                else:
                    label_ids[label] = current_id
                    current_id += 1
                id_ = label_ids[label]
                print(label_ids)

                # now looping through all the image paths and loading the Ids and the images
                # loading the image and converting it to gray scale
                pilImage = Image.open(path).convert('L')
                # Now we are converting the PIL image into numpy array
                imageNp = np.array(pilImage, 'uint8')
                # getting the Id from the image
                # Id = int(os.path.split(imagePath)[-1].split(".")[1])
                # extract the face from the training image sample
                faces.append(imageNp)
                Ids.append(id_)
    return faces, Ids

def FaceRecDisplay(id):
    layout = [
        [sg.Text('USER DETAILS UPDATE', font=('Century Gothic', 18), justification='center', size=(30, 11))],
        [sg.Frame(title='UPDATE DETAILS', layout=[
            [sg.Text('Full Name'), sg.Input('', key='-FLNAME-',disabled=True)],
            [sg.Text('Email ID'), sg.Input('', key='-EMAIL-',disabled=True)],
            [sg.Text('Mobile No'), sg.Input('', key='-MOBILE-',disabled=True)],
            [sg.Text('Address'), sg.Input('', key='-ADDRESS-',disabled=True)],
            [sg.Multiline('', key='-NOTES-')],
            [sg.Button('UPDATE NOTES',key='-UPDATE-'), sg.Exit()]
        ], element_justification='center')]
    ]
    update_user = sg.Window('UPDATE USER', layout, element_justification='center')
    events, values = update_user.Read(timeout=20)
    uid = id
    print(uid)
    con = sqlite3.connect('uservisit.db')
    cur = con.cursor()
    cur.execute("SELECT user.*,Notes.* FROM user,Notes WHERE user.user_id=? AND Notes.user_id=user.user_id",(uid,))
    data = cur.fetchall()
    if len(data) > 0:
        for lol in data:
            update_user['-FLNAME-'].update(lol[1])
            update_user['-EMAIL-'].update(lol[2])
            update_user['-MOBILE-'].update(lol[3])
            update_user['-ADDRESS-'].update(lol[4])
            update_user['-NOTES-'].update(lol[7])
        if events in (None, 'Exit'):
            update_user.Close()
        elif events == '-UPDATE-':
            notes=values['-NOTES-']
            cur.execute("UPDATE Notes SET note=? WHERE user_id=?",(notes,uid))
            con.commit()
            if cur.rowcount==1:
                sg.PopupOK("Notes Updated Successfully")
                update_user.Close()
#update_user.Close()

def FaceRecognition():
    name=''
    date = datetime.utcnow()
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    cap = cv2.VideoCapture(0)

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("Trainer/Trainer.yml")

    labels = {"person_name": 1}
    with open("labels.pickle", "rb") as f:
        labels = pickle.load(f)
        labels = {v: k for k, v in labels.items()}

    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.5, minNeighbors=5)
        for (x, y, w, h) in faces:
            print(x, w, y, h)
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = frame[y:y + h, x:x + w]
            id_, conf = recognizer.predict(roi_gray)
            print("CONFIDENCE:" + str(conf))
            if conf >= 60:
                print(id_)
                print(labels[id_])
                font = cv2.QT_FONT_NORMAL
                id = 0
                id += 1
                name = labels[id_]
                color = (255, 0, 0)
                stroke = 2
                # text2=name+"   "+conf
                cv2.putText(frame, name, (x, y), font, 1, color, stroke, cv2.LINE_AA)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), (2))
                con = sqlite3.connect('uservisit.db')
                cur = con.cursor()
                c = cur.execute(
                    "SELECT user.*,Notes.* FROM user,Notes WHERE user.user_id=? AND Notes.user_id=user.user_id",
                    (name,))
                result = cur.fetchall()
                #print(result)
                cv2.rectangle(frame, (30, 30), (300,190), (0, 0, 0),-1)
                for lol in result:
                    cv2.putText(frame, "Name: "+lol[1], (50, 50),cv2.FONT_HERSHEY_PLAIN, 1, (225,225,225), 1)
                    cv2.putText(frame,"Email: "+lol[2],(50,80),cv2.FONT_HERSHEY_PLAIN, 1, (225,225,225), 1)
                    cv2.putText(frame,"Mobile: "+lol[3],(50,110),cv2.FONT_HERSHEY_PLAIN, 1, (225,225,225), 1)
                    cv2.putText(frame,"Address: "+lol[4],(50,140),cv2.FONT_HERSHEY_PLAIN, 1, (225,225,225), 1)
                    cv2.line(frame,(30,151),(300,151),(0,0,225),thickness=2,lineType=cv2.LINE_4)
                    cv2.putText(frame,"Notes: "+lol[7],(50,180),cv2.FONT_HERSHEY_PLAIN, 1, (225,225,225), 1)
            else:
                color = (255, 0, 0)
                stroke = 2
                font = cv2.QT_FONT_NORMAL
                cv2.putText(frame, "UNKNOWN", (x, y), font, 1, color, stroke, cv2.LINE_AA)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), (2))
        cv2.imshow('Visitor', frame)
        k = cv2.waitKey(20) & 0xff
        if k == ord('q'):
            break
        elif k==ord('v'):
            FaceRecDisplay(name)
    cap.release()
    cv2.destroyAllWindows()


#FaceRecognition()
