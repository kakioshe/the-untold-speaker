import boto3
import random
import pyaudio
import wave
import time
import os

def playAudio(fileName, channel = 2):
    chunk = 1024
    wf = wave.open(fileName, 'rb')
    p = pyaudio.PyAudio()

    form_1 = pyaudio.paInt16
    chans = channel
    samp_rate = 44100
    chunk = 4096
    dev_index = 2

    stream = p.open(
        format = form_1,
        channels = chans,
        rate = samp_rate,
        frames_per_buffer = chunk,
        output_device_index = dev_index,
        output = True)
    data = wf.readframes(wf.getnframes())

    stream.start_stream()
    stream.write(data)
    time.sleep(0.2)
    stream.close()
    p.terminate()

    return True

def downloadFile(bucketName, emotion, fileName):
    s3 = boto3.resource('s3',
                        aws_access_key_id = os.environ['ACCESS_ID'],
                        aws_secret_access_key = os.environ['ACCESS_KEY'])
    s3_client = boto3.client('s3',
                        aws_access_key_id = os.environ['ACCESS_ID'],
                        aws_secret_access_key = os.environ['ACCESS_KEY'])

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

    n = 0
    for audio in randomizedFiles:
        audioName = 'sound/' + audio
        if n == 0:
            s3_client.download_file(bucketName, audio, audioName)
        try:
            playAudio(audioName, 1)
        except:
            print("file didn't exist")
            s3_client.download_file(bucketName, audio, audioName)
            playAudio(audioName, 1)
        n += 1
    return True
