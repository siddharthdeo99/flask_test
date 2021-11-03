from flask import Flask,render_template,Response
import cv2
from cvzone.HandTrackingModule import HandDetector
from time import sleep
import numpy as np
import cvzone
from pynput.keyboard import Controller

app=Flask(__name__)
cap=cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
            
detector = HandDetector(detectionCon=0.8)
keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"]]
finalText = ""

            
keyboard = Controller()
def drawAll(img, buttonList):
    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        cvzone.cornerRect(img, (button.pos[0], button.pos[1], button.size[0], button.size[1]),
                          20, rt=0)
        cv2.rectangle(img, button.pos, (x + w, y + h), (255, 0, 255), cv2.FILLED)
        cv2.putText(img, button.text, (x + 20, y + 65),
                    cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
    return img
class Button():
    def __init__(self, pos, text, size=[85, 85]):
        self.pos = pos
        self.size = size
        self.text = text
 
 
buttonList = []
for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
        buttonList.append(Button([100 * j + 50, 100 * i + 50], key))

def generate_frames(finalText):
    while True:
        success,img=cap.read()
        if not success:
            break
        else:
            img = detector.findHands(img)
            lmList, bboxInfo = detector.findPosition(img)
            img = drawAll(img, buttonList)
            
            if lmList:
                for button in buttonList:
                    x, y = button.pos
                    w, h = button.size
        
                    if x < lmList[8][0] < x + w and y < lmList[8][1] < y + h:
                        cv2.rectangle(img, (x - 5, y - 5), (x + w + 5, y + h + 5), (175, 0, 175), cv2.FILLED)
                        cv2.putText(img, button.text, (x + 20, y + 65),
                                    cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                        l, _, _ = detector.findDistance(8, 12, img, draw=False)
                        print(l)
        
                        ## when clicked
                        if l < 30:
                            keyboard.press(button.text)
                            cv2.rectangle(img, button.pos, (x + w, y + h), (0, 255, 0), cv2.FILLED)
                            cv2.putText(img, button.text, (x + 20, y + 65),
                                        cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                            finalText += button.text
                            sleep(0.15)
        
            cv2.rectangle(img, (50, 350), (700, 450), (175, 0, 175), cv2.FILLED)
            cv2.putText(img, finalText, (60, 430),
                        cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)
            
            cv2.waitKey(1)      
            
            
            ret,buffer=cv2.imencode('.jpg',img)
            img = buffer.tobytes()
        yield(b'--img\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + img + 
                    b'\r\n')
            




@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(generate_frames(finalText),mimetype='multipart/x-mixed-replace; boundary=img')

if __name__ == "__main__":
    app.run(debug=False,host='0.0.0.0')
