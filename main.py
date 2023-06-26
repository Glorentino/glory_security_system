import threading
from winsound import Beep
import cv2
import imutils
from deepface import DeepFace
from datetime import datetime


capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Creates the camera
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

_, start_frame = capture.read()
start_frame = imutils.resize(start_frame, width=500)
start_frame = cv2.cvtColor(start_frame, cv2.COLOR_BGR2GRAY)
start_frame = cv2.GaussianBlur(start_frame, (21, 21), 0)

alarm = False
alarm_mode = False
alarm_counter = 0 
face_counter = 0

face_match = False
face_match_name = ""

# Verifies that we recognize the face on frame
def check_face(frame):
    global face_match, face_match_name
    imageList = ["ref.jpg", "ref1.jpg"]
    for img in imageList:
        reference_img = cv2.imread(img)
        try:
            if DeepFace.verify(frame, reference_img.copy())['verified']:
                face_match = True
                face_match_name = img
                with open("facelog.txt","a") as log:
                    log.write(f"{img} detected at {datetime.now()} \n")
                break
            else:
                face_match = False
        except ValueError:
            face_match = False

#triggers alarm
def beep_alarm():
    global alarm

    for _ in range(2):
        if not alarm_mode:
            break
        print("ALARM")
        Beep(2500, 3000)
    alarm = False

while True:
    ret, frame = capture.read()
    if ret:
        if face_counter % 30 == 0:
            try:
                threading.Thread(target=check_face, args=(frame.copy(),)).start()
            except ValueError:
                pass
        face_counter += 1

        if face_match:
            cv2.putText(frame, f"MATCH! {face_match_name}", (20, 450), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 3)
        else:
            cv2.putText(frame, "NO MATCH!", (20, 450), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 0, 255), 3)


    frame = imutils.resize(frame, width=500)

    # When in alarm mode, the frame turns grays and tracks movement

    if alarm_mode:
        frame_bw = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_bw = cv2.GaussianBlur(frame_bw, (5, 5), 0)

        difference = cv2.absdiff(frame_bw, start_frame)
        threshold = cv2.threshold(difference, 25, 255, cv2.THRESH_BINARY)[1]
        start_frame = frame_bw

        if threshold.sum() > 10000: # Tracks movement
            alarm_counter += 1
        else:
            if alarm_counter > 0:
                alarm_counter -= 1
        cv2.imshow("Cam", threshold)
    else:
        cv2.imshow("Cam", frame)

    
    if alarm_counter > 20:
        if not alarm:
            alarm = True

            with open("log.txt","a") as log:
                log.write(f"Motion detected at {datetime.now()} \n")
                
            threading.Thread(target=beep_alarm).start()
    
    key_pressed = cv2.waitKey(30)
    if key_pressed == ord("t"):
        alarm_mode = not alarm_mode
        alarm_counter = 0
    if key_pressed == ord("q"):
        alarm_mode = False
        break
capture.release()
cv2.destroyAllWindows()
