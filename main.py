import requests
import time
import RPi.GPIO as GPIO
from input import *
from fileDownload import downloadFile, playAudio
import os
import board
import neopixel


pixel_pin = board.D18
num_pixels = 2
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.5, auto_write=False,
                           pixel_order=ORDER)

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
    
def colorChange(emotion):
    #if(emotion == 'Sadness'):
    for i in range(50,250):
        for j in range(36):
            pixels[j] = (0,i,0)
            pixels[j+1] = (i,i,i)
        pixels.show()
        time.sleep(0.000000001)
    for i in range (250,50,-1):
        for j in range(36):
            pixels[j] = (0,i,0)
            pixels[j+1] = (i,i,i)
        pixels.show()
    
    
def main():
    STATUS_LIST = ["idle", "speaker", "listener", "feedback"]
    HEROKU_URL = "http://the-untold.herokuapp.com/status/5cc1ab8dfb6fc0265f2903a3"
    bucket = 'the-untold'
    status = ''
    
    while status == '':
        try:
            status = updateStatus()
        except:
            print('reconnecting')
    requests.put(HEROKU_URL, json={
        "status": STATUS_LIST[0],
        })        
    
    while True:
        #Do infinite loop, catch current status each loop
        
        if status != STATUS_LIST[0]:
            
            
            status = updateStatus()
            if status == STATUS_LIST[1]:
                print("SPEAKER Speaker currently speaking")
                # DO THE RECORDING, and EMOTION DETECTOR CODE HERE
                try:
                    #pixels.fill((0,255,0))
                    #pixels.show()
                    
                    if (GPIO.input(26) == 1):
                        record()
                        #pixels.fill((255,0,0))
                        #pixels.show()
                        emotion = detect_emotions(speech_to_text("story.wav"))
                        playAudio('sound/voiceover/2.1.wav')
                        os.remove("story.wav")
                        print(emotion[0])
                        print(len(emotion))
                        if ((len(emotion) == 0) or emotion[0][0] == "Analytical" or
                            emotion[0][0] == "Confident" or emotion[0][0] == "Tentative"):
                            playAudio('sound/voiceover/3.1.wav')
                            print("And how does that makes you feel?")
                        else:
                            print("moving on")
                            #could be improved by making a function
                            if (emotion[0][0] == "Sadness"):
                                playAudio('sound/voiceover/4a.1.wav')
                            elif (emotion[0][0] == "Anger"):
                                playAudio('sound/voiceover/5.1.wav')
                            elif (emotion[0][0] == "Fear"):
                                playAudio('sound/voiceover/6.1.wav')
                            elif (emotion[0][0] == "Joy"):
                                playAudio('sound/voiceover/7.1.wav')
                            
                            playAudio('sound/voiceover/8a.2.wav')
                            playAudio('sound/voiceover/8.1.wav')
                            requests.put(HEROKU_URL, json={
                                "status": STATUS_LIST[2],
                                "emotion": emotion[0][0],
                                "score": emotion[0][1]
                                })
                except:
                    print("Could you repeat that again?")
                    playAudio('sound/voiceover/3.1.wav')
                
                
            elif status == STATUS_LIST[2]:
                #WHILE LOOP THE COLOR BLEEPING THINGS
                for x in range(5):
                    colorChange(r.json()[0]['emotion'])
                print("SPEAKER Listener currently making a feedback")
                time.sleep(2)
                #DO play recorded msg

            elif status == STATUS_LIST[3]:
                print("SPEAKER Playing the feedback and other msgs")
                r = requests.get('http://the-untold.herokuapp.com/status')
                playAudio('sound/voiceover/12.1.wav')
                filename = r.json()[0]['filename']
                emotion = r.json()[0]['emotion']
                print("filename is {}".format(filename))
                #download file should only download latest file. other data
                #will be stored locally to save bandwidth
                downloadFile(bucket, emotion, filename)
                
                #closing statements
                if emotion == "Sadness":
                    playAudio('sound/voiceover/14.1.wav')
                elif emotion == "Depression":
                    playAudio('sound/voiceover/14a.1.wav')
                elif emotion == "Anger":
                    playAudio('sound/voiceover/15.1.wav')
                elif emotion == "Fear":
                    playAudio('sound/voiceover/16.1.wav')
                elif emotion == "Joy":
                    playAudio('sound/voiceover/17.1.wav')
                
                playAudio('sound/voiceover/18.1.wav')
                requests.put(HEROKU_URL, json={
                    "status": STATUS_LIST[0],
                    })
        else:
            print('idle')
            pixels.fill((255,0,0))
            pixels.show()
            if (GPIO.input(26) == 1):
                print("button press")
                playAudio('sound/voiceover/1.1.wav')
                requests.put(HEROKU_URL, json={
                    "status": STATUS_LIST[1],
                    })
                print('test')
                status = updateStatus()

                
            
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(26,GPIO.IN,pull_up_down = GPIO.PUD_DOWN)

main()
