import requests
import time
import RPi.GPIO as GPIO
from input import *
from fileDownload import downloadFile, playAudio
import os
import board
import neopixel


pixel_pin = board.D18
num_pixels = 50
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.1, auto_write=False,
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
    
def colorChange(emotion,score):
    intensity = int(score * 10)
    timesleep = 0.005 / score
    playwhichaudio = ''
    pixels.fill((50,0,50))
    pixels.show()

    
def main():
    pixels.fill((0,0,0))
    pixels[49] = (0,255,0)
    pixels[48] = (0,255,0)
    pixels[47] = (0,255,0)
    pixels[46] = (0,255,0)
    pixels[45] = (0,255,0)
    pixels[44] = (0,255,255)
    pixels[43] = (0,255,255)
    pixels.show()

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
                    if (GPIO.input(26) == 1):
                        print("button press")
                        for i in range(7):
                            pixels[i+36] = (180,0,0)
                            pixels.show()
                        time.sleep(0.5)
                        record()
                        for i in range(7):
                            pixels[i+36] = (0,0,0)
                            pixels.show()
                        playAudio('sound/voiceover/2.1.wav',)
                        emotion = detect_emotions(speech_to_text("story.wav"))
                        detected_emotion = emotion[0][0]
                        detected_score = emotion[0][1]
                        print(emotion)
                        print('checkpoint')
                        os.remove("story.wav")
                        print(detected_score)
                        print(len(emotion))
                        if ((len(emotion) == 0) or emotion[0][0] == "Analytical" or
                            emotion[0][0] == "Confident" or emotion[0][0] == "Tentative"):
                            playAudio('sound/voiceover/3.3.wav')
                            print("And how does that makes you feel?")
                        else:
                            print("moving on")
                            
                            colorChange(detected_emotion,detected_score)
                            playAudio('sound/voiceover/8a.2.wav')
                            playAudio('sound/voiceover/8.1.wav')
                            requests.put(HEROKU_URL, json={
                                "status": STATUS_LIST[2],
                                "emotion": emotion[0][0],
                                "score": emotion[0][1]
                                })
                            tempEmotion = emotion[0][0]
                except:
                    print("Could you repeat that again?")
                    playAudio('sound/voiceover/3.3.wav')
                
                
            elif status == STATUS_LIST[2]:
                #WHILE LOOP THE COLOR BLEEPING THINGS
                #for x in range(5):
                #    colorChange(tempEmotion)
                print(tempEmotion)
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
                pixels.fill((0,0,0))
                pixels[43] = (255,255,255)
                pixels[44] = (255,255,255)
                pixels[49] = (0,255,0)
                pixels[48] = (0,255,0)
                pixels[47] = (0,255,0)
                pixels[46] = (0,255,0)
                pixels[45] = (0,255,0)
                pixels.show()
        else:
            print('idle')
            print(pixels.show())
            if (GPIO.input(26) == 1):
                pixels[49] = (255,0,0)
                pixels[48] = (255,0,0)
                pixels[47] = (255,0,0)
                pixels[46] = (255,0,0)
                pixels[45] = (255,0,0)
                print(pixels)
                for r in range(2):
                    for i in range(7):
                        pixels[i+36] = (250,0,0)
                        pixels.show()
                    time.sleep(0.3)
                    for i in range(7):
                        pixels[i+36] = (250,250,0)
                        pixels.show()
                    time.sleep(0.3)
                    for i in range(7):
                        pixels[i+36] = (0,250,0)
                        pixels.show()
                    time.sleep(0.3)
                    for i in range(7):
                        pixels[i+36] = (0,0,250)
                        pixels.show()
                    time.sleep(0.3)
                    for i in range(7):
                        pixels[i+36] = (0,0,0)
                        pixels.show()
                print("button press")
                requests.put(HEROKU_URL, json={
                    "status": STATUS_LIST[1],
                    })
                print('test')
                status = updateStatus()
                playAudio('sound/voiceover/1.2.wav',2)
                playAudio('sound/voiceover/19.2.wav',2)
            time.sleep(1)
                
            
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(26,GPIO.IN,pull_up_down = GPIO.PUD_DOWN)

main()
