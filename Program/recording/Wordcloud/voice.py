import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pyaudio
import wave
import boto3
import time
import datetime
import json
import urllib.request

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 60
WAVE_OUTPUT_FILENAME = "output.wav"

ACCESS_KEY = 'AKIAW24HYOAV4N3SUVMD'
SECRET_KEY = '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'
BUCKET_NAME = 'songleesim'


# 녹음

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("Start to record the audio.")

frames = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("Recording is finished.")

stream.stop_stream()
stream.close()
p.terminate()

wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()


# Upload

# S3 Client 생성
s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)

s3.upload_file(WAVE_OUTPUT_FILENAME, BUCKET_NAME, WAVE_OUTPUT_FILENAME)

# %%

# Transcribe

job_name = "test_transcribe" + str(datetime.datetime.now())[-6:]
job_uri = "s3://" + BUCKET_NAME + "/" + WAVE_OUTPUT_FILENAME

transcribe = boto3.client('transcribe', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY,
                          region_name="ap-northeast-2")
transcribe.start_transcription_job(
    TranscriptionJobName=job_name,
    Media={'MediaFileUri': job_uri},
    MediaFormat='wav',
    MediaSampleRateHertz=RATE,
    LanguageCode='ko-KR'
)

elapsed_time = 0
while True:
    status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
    if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
        break

    if elapsed_time == 0:
        print("Transcription start...")
    else:
        print("Not ready yet. " + str(elapsed_time) + "sec passed.")

    time.sleep(5)
    elapsed_time += 5

print(status)


# Transcript Result File

transcript_file_uri = status["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
print(transcript_file_uri)
result = ""

with urllib.request.urlopen(transcript_file_uri) as url:
    tr_json = json.loads(url.read().decode())
    tr_list = tr_json['results']['transcripts']

    for tr_item in tr_list:
        print(tr_item['transcript'])
        result += tr_item['transcript']


# wordcloud
font_path = 'SDSwaggerTTF.ttf'
wordcloud = WordCloud(font_path=font_path, width=1200, height=1200,
                      background_color='black').generate(result)

plt.figure(figsize=(12, 12), facecolor='k')
plt.imshow(wordcloud)
plt.axis("off")
plt.tight_layout(pad=0)

# plt.show()
plt.savefig('wordcloud_without_axisoff2.png', facecolor='k', bbox_inches='tight')
