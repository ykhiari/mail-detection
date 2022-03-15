# imports
from scripts.notifier import TwilioNotifier
import numpy as np
from datetime import datetime
from datetime import date
import argparse
import signal
import json
import sys
import cv2
import time
import imutils

# helper function to exit the system
def signal_handler(sig, frame):
    print("You pressed 'ctrl+c', Closing the app... ")
    cap.release()
    sys.exit(0)

# argument parser to the script
parser = argparse.ArgumentParser()
parser.add_argument("-c","--conf", required=True, help="path to the conf file")
args = vars(parser.parse_args())

# load the conf file
with open(args["conf"],"r") as jsonfile:
    conf = json.load(jsonfile)
    
# initialize a notifier
tn = TwilioNotifier(conf)

# initialize flags
mailboxOpen = False
notifSent = False

# initialize the video streamer
print("warming up camera...")
cap = cv2.VideoCapture(0)
time.sleep(2)

# signal trap to handle keyboard interrupt
signal.signal(signal.SIGINT, signal_handler)
print("Press 'ctrl+c' to exit the script.")

# starting the camera
# while True:
#     # reading frame, resize it and then change color to gray
#     _, frame = cap.read()
#     resized = imutils.resize(frame, width=200)
#     gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    
#     # set the previous mailbox status
#     mailboxPrevOpen = mailboxOpen
    
#     mean = np.mean(gray)
#     mailboxOpen = mean > conf["thresh"]
    
#     if mailboxOpen and not mailboxPrevOpen:
#         print("here")
#         startTime = datetime.now()
#     elif mailboxPrevOpen:
#         elapsedTime = (datetime.now() - startTime).seconds
#         mailboxLeftOpen = elapsedTime > conf["open_threshold_seconds"]
#         if mailboxOpen and mailboxLeftOpen:
#             if not notifSent:
#                 msg = f"Your mailbox at {conf['twilio_id']} has been left open for longer than {elapsedTime} seconds"
#                 tn.send(msg)
#                 notifSent = True
#         elif not mailboxOpen:
#             if notifSent:
#                 notifSent = False
#             else:
#                 endTime = datetime.now()
#                 totalSeconds = (endTime - startTime).seconds
#                 dateOpened = date.today().strftime("%A, %B %d %Y")
#                 msg = f"Your mailbox at {conf['twilio_id']} was opened at {startTime} for {totalSeconds} seconds"
#                 tn.send(msg)
#     if conf['display']:
#         cv2.imshow('frame',frame)
#         key = cv2.waitKey(1) & 0xFF
#         if key == ord('q'):
#             break
state = False
notified = False
while True:
    previous = state
    _, frame = cap.read()
    if conf['display']:
        cv2.imshow('frame',frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
    resized = imutils.resize(frame, width=200)
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    mean = np.mean(gray)
    mailboxOpen = mean > conf["thresh"]
    
    if mailboxOpen and not previous:
        startTime = datetime.now()
        state = True
        notified = False
        previous = state
        
    
    if mailboxOpen:
        if previous:
            elapsed = (datetime.now() - startTime).seconds
            if elapsed > conf['open_threshold_seconds'] and not notified:
                msg = f"mail box open for long time {elapsed}"
                tn.send(msg)
                notified = True
            else:
                continue
    else:
        if state and not notified:
            endTime = datetime.now()
            msg = f"mail box has been opened and closed at {endTime}"
            tn.send(msg)
            notified = True
            state = False
        else:
            continue
    




cv2.destroyAllWindows()
cap.release()