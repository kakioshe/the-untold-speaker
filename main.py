import requests
import time

# SPEAKER SIDE
# Status List:
# 1. idle = Initial status, when no one is inside the booth
# 2. speaker = When the speaker is currently speaking
# 3. listener = When the speaker has finished speaking, the emotion will
#               be sent to the listener. Listener side will read the emotion
#               and ask for feedback. Speaker side will play a pre-recorded msg
# 4. feedback = When the listener has finished saying feedback, and its uploaded
#               speaker side will play that feedback and some pre-recorded msg

def main():
    STATUS_LIST = ["idle", "speaker", "listener", "feedback"]
    HEROKU_URL = "http://the-untold.herokuapp.com/status/5cc1ab8dfb6fc0265f2903a3"
    while True:
        #Do infinite loop, catch current status each loop
        r = requests.get('http://the-untold.herokuapp.com/status')
        status = r.json()[0]['status']
        
        if status == STATUS_LIST[1]:
            print("SPEAKER Speaker currently speaking")
            # DO THE RECORDING, and EMOTION DETECTOR CODE HERE
            time.sleep(10)
            emotion = "sad"
            requests.put(HEROKU_URL, json={
                "status": STATUS_LIST[2],
                "emotion": emotion
                })
            
        elif status == STATUS_LIST[2]:
            print("SPEAKER Listener currently making a feedback")
            #DO play recorded msg

        elif status == STATUS_LIST[3]:
            print("SPEAKER Playing the feedback and other msgs")
            filename = r.json()[0]['filename']
            print("filename is {}".format(filename))
            #DO play feedback and other recorded msg
            time.sleep(10)
            requests.put(HEROKU_URL, json={
                "status": STATUS_LIST[0],
                })

        else:
            print("idling")

main()
