import boto3
import random
import pyaudio
import wave
import time
import os

def playAudio(fileName):
    chunk = 1024
    wf = wave.open(fileName, 'rb')
    p = pyaudio.PyAudio()

    stream = p.open(
        format = p.get_format_from_width(wf.getsampwidth()),
        channels = wf.getnchannels(),
        rate = wf.getframerate(),
        output = True)
    data = wf.readframes(wf.getnframes())

    stream.start_stream()
    stream.write(data)
    time.sleep(0.2)
    stream.close()
    p.terminate()
    return True

def downloadFile(bucketName, emotion, fileName):
    s3 = boto3.resource('s3')
    s3_client = boto3.client('s3')
    
    myBucket = s3.Bucket(bucketName)
    fileDir = "{}/{}".format(emotion,fileName)
    files = []

    for file in myBucket.objects.filter(Delimiter='/', Prefix='{}/'.format(emotion)):
        if len(file.key.split("/")[1]) > 0:
            files.append(file.key)

    maxLength = 5 if len(files) > 5 else len(files)
    print(files)
    randomizedFiles = [fileDir]
    while len(randomizedFiles) < maxLength:
        x = random.randint(1,len(files))
        if (files[x-1] not in randomizedFiles):
            randomizedFiles.append(files[x-1])

    print(randomizedFiles)
    for audio in randomizedFiles:
        audioName = audio.split("/")[1]
        print("length : ",len(audioName))
        print(audioName)
        s3_client.download_file(bucketName, audio, audioName)
        playAudio(audioName)
        os.remove(audioName)
    return True

