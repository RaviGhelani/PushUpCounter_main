import cv2
import mediapipe as mp
import numpy as np
import PoseModule as pm
from pymongo import MongoClient # import mongo client to connect
import pprint
# Creating instance of mongoclient
client = MongoClient()
# Creating database
db = client["PushUp"]
employee=db["a"]

cap = cv2.VideoCapture(0)
detector = pm.poseDetector()
count = 0
direction = 0
form = 0
feedback = "Fix Form"

while cap.isOpened():
    ret, img = cap.read() #640 x 480
    #Determine dimensions of video - Help with creation of box in Line 43
    width  = cap.get(3)  # float `width`
    height = cap.get(4)  # float `height`
    # print(width, height)
    
    img = detector.findPose(img, False)
    lmList = detector.findPosition(img, False)
    # print(lmList)
    if len(lmList) != 0:
        elbow_left = detector.findAngle(img, 11, 13, 15)
        elbow_right = detector.findAngle(img, 12, 14, 16)
        leg_left = detector.findAngle(img,24,26,28)
        temp = []
        temp = lmList[13][2]
        """shoulder = detector.findAngle(img, 13, 11, 23)
        hip = detector.findAngle(img, 11, 23,25)"""


        
        #Percentage of success of pushup
        per_left = np.interp(elbow_left, (90, 160), (0, 100))
        per_right = np.interp(elbow_right, (90, 160), (0, 100))

        #Bar to show Pushup progress
        bar_left = np.interp(elbow_left, (90, 160), (380, 50))
        bar_right = np.interp(elbow_right, (90, 160), (380, 50))

        #Check to ensure right form before starting the program
        if elbow_left < 50 and elbow_right<50:
            form = 1
        # elif elbow_left<50:
        #     form = 2
        # elif elbow_right<50:
        #     form = 3
        # elif leg_left<80:
        #     form = 4
        #
        # if leg_left < 50:
        #     form = 4
        #Check for full range of motion for the pushup
        if form == 1:
            #if per_left == 0 and  per_right==0:
                if elbow_left <= 90 and elbow_right<=90:
                    feedback = "Up"
                    if direction == 0:
                        count += 0.5
                        direction = 1
                else:
                    feedback = "Fix Form"

            #if per_left == 100 and per_right==100:
                if elbow_left > 160 and elbow_right>160:
                    feedback = "Down"
                    if direction == 1:
                        count += 0.5
                        direction = 0
                        Data ={
                          "pushup_data": temp
                        }
                        print(temp)

                        # Creating document
                        MyData = db.employees
                        # Inserting data
                        MyData.insert_one(Data)
                else:
                    feedback = "Fix Form"
                        # form = 0

        # Check for full range of motion for the pushup
        if form == 2:
            # if per_left == 0 and  per_right==0:
            if elbow_left <= 90:
                feedback = "Up"
                if direction == 0:
                    count += 0.5
                    direction = 1
            else:
                feedback = "Fix Form"

            # if per_left == 100 and per_right==100:
            if elbow_left > 160:
                feedback = "Down"
                if direction == 1:
                    count += 0.5
                    direction = 0
            else:
                feedback = "Fix Form"
                # form = 0

        # Check for full range of motion for the pushup
        if form == 3:
            # if per_left == 0 and  per_right==0:
            if elbow_right <= 90:
                feedback = "Up"
                if direction == 0:
                    count += 0.5
                    direction = 1
            else:
                feedback = "Fix Form"

            # if per_left == 100 and per_right==100:
            if elbow_right > 160:
                feedback = "Down"
                if direction == 1:
                    count += 0.5
                    direction = 0
            else:
                feedback = "Fix Form"
                # form = 0

        # Check for full range of motion for the pushup
        if form == 4:
            # if per_left == 0 and  per_right==0:
            if leg_left >= 140:
                feedback = "Up"
                if direction == 0:
                    count += 0.5
                    direction = 1
            else:
                feedback = "Fix Form"

            # if per_left == 100 and per_right==100:
            if leg_left < 80:
                feedback = "Down"
                if direction == 1:
                    count += 0.5
                    direction = 0
            else:
                feedback = "Fix Form"
                # form = 0

        print(count)

        #Draw Bar

        if form==3:
            cv2.rectangle(img, (580, 50), (600, 380), (0, 255, 0), 3)
            cv2.rectangle(img, (580, int(bar_right)), (600, 380), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, f'{int(per_right)}%', (565, 430), cv2.FONT_HERSHEY_PLAIN, 2,
                        (255, 0, 0), 2)

        if form==1 or form==2:
            cv2.rectangle(img, (580, 50), (600, 380), (0, 255, 0), 3)
            cv2.rectangle(img, (580, int(bar_left)), (600, 380), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, f'{int(per_left)}%', (565, 430), cv2.FONT_HERSHEY_PLAIN, 2,
                        (255, 0, 0), 2)

        #Pushup counter
        cv2.rectangle(img, (0, 380), (100, 480), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, str(int(count)), (25, 455), cv2.FONT_HERSHEY_PLAIN, 5,
                    (255, 0, 0), 5)
        
        #Feedback
        cv2.rectangle(img, (500, 0), (640, 40), (255, 255, 255), cv2.FILLED)
        cv2.putText(img, feedback, (500, 40 ), cv2.FONT_HERSHEY_PLAIN, 2,
                    (0, 255, 0), 2)

    """if (lmList[25][2] and lmList[26][2] >= lmList[23][2] and lmList[24][2]):
        posiotion = "sit"
    if (lmList[25][2] and lmList[26][2] <= lmList[23][2] and lmList[24][2] and posiotion == "sit"):
        posiotion = "up"
        count += 1
        print("tirth")
        print(count)"""

    cv2.imshow('Pushup counter', img)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break
        
cap.release()
cv2.destroyAllWindows()