import requests
import time
import RPi.GPIO as GPIO
from input import *
from fileDownload import downloadFile
import os

# SPEAKER SIDE
# Status List:
# 1. idle = Initial status, when no one is inside the booth
# 2. speaker = When the speaker is currently speaking
# 3. listener = When the speaker has finished speaking, the emotion will
#               be sent to the listener. Listener side will read the emotion
#               and ask for feedback. Speaker side will play a pre-recorded msg
# 4. feedback = When the listener has finished saying feedback, and its uploaded
#               speaker side will play that feedback and some pre-recorded msg

def updateStatus():
    r = requests.get('http://the-untold.herokuapp.com/status')
    return r.json()[0]['status']
    

def main():
    print("ready")
    STATUS_LIST = ["idle", "speaker", "listener", "feedback"]
    HEROKU_URL = "http://the-untold.herokuapp.com/status/5cc1ab8dfb6fc0265f2903a3"
    bucket = 'the-untold'
    status = updateStatus()
    
    while True:
        #Do infinite loop, catch current status each loop
        
        if status != STATUS_LIST[0]:
            
            
            status = updateStatus()
            if status == STATUS_LIST[1]:
                print("SPEAKER Speaker currently speaking")
                # DO THE RECORDING, and EMOTION DETECTOR CODE HERE
                #record()
                #emotion = detect_emotions(speech_to_text("story.wav"))
                #os.remove("story.wav")
                emotion = "Sadness"
                requests.put(HEROKU_URL, json={
                    "status": STATUS_LIST[2],
                    "emotion": emotion
                    })
                
            elif status == STATUS_LIST[2]:
                print("SPEAKER Listener currently making a feedback")
                time.sleep(2)
                #DO play recorded msg

            elif status == STATUS_LIST[3]:
                print("SPEAKER Playing the feedback and other msgs")
                r = requests.get('http://the-untold.herokuapp.com/status')
                filename = r.json()[0]['filename']
                emotion = r.json()[0]['emotion']
                print("filename is {}".format(filename))
                #DO play feedback and other recorded msg
                downloadFile(bucket, emotion, filename)
                requests.put(HEROKU_URL, json={
                    "status": STATUS_LIST[0],
                    })
        else:
            if (GPIO.input(26) == 1):
                print("button press")
                requests.put(HEROKU_URL, json={
                    "status": STATUS_LIST[1],
                    })        
                status = updateStatus()

                
            
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(26,GPIO.IN,pull_up_down = GPIO.PUD_DOWN)

main()
