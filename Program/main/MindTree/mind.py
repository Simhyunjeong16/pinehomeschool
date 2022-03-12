from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from main_window_ import *
import main_window_
from main_window_2 import *
import main_window_2
import aaaa
from ui_main_window import *
import pygame
import eyetracking
from eyetracking import *
import main_window
from main_window import *
import box
from box import *
import graph
from graph import *
import sys
import boto3

import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pyaudio
import wave
import time
import datetime
import json
import urllib.request

connection = pymysql.connect(host='203.252.208.222', user='root', password='MindTree@12345', db='imageupload', port=8008)

with connection.cursor() as cursor:  # 아이 이름
    sql = "select childname from images ORDER BY id DESC limit 1"
    cursor.execute(sql)
    childrenname = cursor.fetchone()
    print("아이 이름 :", childrenname[0])

if childrenname[0] == "":
    name = '친구'
else:
    name = childrenname[0]

## 링크 참고하여 개발  ##  https://github.com/letsgo247/under-checker/blob/master/%EB%B0%9B%EC%B9%A8%20%ED%8C%90%EB%8B%A8%EA%B8%B0.py

def under_checker(word):    #아스키(ASCII) 코드 공식에 따라 입력된 단어의 마지막 글자 받침 유무를 판단해서 뒤에 붙는 조사를 리턴하는 함수
    last = word[-1]     #입력된 word의 마지막 글자를 선택해서
    criteria = (ord(last) - 44032) % 28     #아스키(ASCII) 코드 공식에 따라 계산 (계산법은 다음 포스팅을 참고하였습니다 : http://gpgstudy.com/forum/viewtopic.php?p=45059#p45059)
    if criteria == 0:       #나머지가 0이면 받침이 없는 것
        return word +'야'
    else:                   #나머지가 0이 아니면 받침 있는 것
        return word+'아'

call_name = under_checker(name)
## ㄴ 가져온 단어의 마지막 글자 받침 유무를 판단하는 코드 ##

emo_quiz_voice = call_name + ', 내가 지금 무슨 감정일까?'
# emo_follow_voice = call_name + ', 내 표정을 따라해봐!' ## 혹시 소리 렉 안 먹으면 하자!!!
# look_voice = call_name + ', 내 눈에 썬글라스를 씌워줘!'

polly_client = boto3.Session(
                aws_access_key_id='AKIAW24HYOAV4N3SUVMD',
    aws_secret_access_key='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',
    region_name='ap-northeast-2').client('polly')

# response = polly_client.synthesize_speech(VoiceId='Seoyeon',
#                 OutputFormat='mp3',
#                 Text = emo_follow_voice)
#
# file = open('emo_follow_voice.mp3', 'wb')
# file.write(response['AudioStream'].read())
# file.close()

response2 = polly_client.synthesize_speech(VoiceId='Seoyeon',
                OutputFormat='mp3',
                Text = emo_quiz_voice)

file = open('emo_quiz_voice.mp3', 'wb')
file.write(response2['AudioStream'].read())
file.close()

# response3 = polly_client.synthesize_speech(VoiceId='Seoyeon',
#                 OutputFormat='mp3',
#                 Text = look_voice)
#
# file = open('look_voice.mp3', 'wb')
# file.write(response3['AudioStream'].read())
# file.close()

class PicButton(QAbstractButton):
    def __init__(self, pixmap, parent=None):
        super(PicButton, self).__init__(parent)
        self.pixmap = pixmap

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

    def sizeHint(self):
        return self.pixmap.size()

# class Voice_record(QObject):
#     signalExample = QtCore.pyqtSignal()
#
#     def __init__(self, parent=None):
#         super(self.__class__, self).__init__(parent)
#
#     @QtCore.pyqtSlot()
#     def voice(self):
#         CHUNK = 1024
#         FORMAT = pyaudio.paInt16
#         CHANNELS = 1
#         RATE = 44100
#         RECORD_SECONDS = 20 #120초임.
#         WAVE_OUTPUT_FILENAME = "output.wav"
#
#         ACCESS_KEY = 'AKIAW24HYOAV4N3SUVMD'
#         SECRET_KEY = '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'
#         BUCKET_NAME = 'songleesim'
#
#         # 녹음
#
#         p = pyaudio.PyAudio()
#
#         stream = p.open(format=FORMAT,
#                         channels=CHANNELS,
#                         rate=RATE,
#                         input=True,
#                         frames_per_buffer=CHUNK)
#
#         print("Start to record the audio.")
#
#         frames = []
#
#         for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
#             data = stream.read(CHUNK)
#             frames.append(data)
#
#         print("Recording is finished.")
#
#         stream.stop_stream()
#         stream.close()
#         p.terminate()
#
#         wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
#         wf.setnchannels(CHANNELS)
#         wf.setsampwidth(p.get_sample_size(FORMAT))
#         wf.setframerate(RATE)
#         wf.writeframes(b''.join(frames))
#         wf.close()
#
#         # Upload
#
#         # S3 Client 생성
#         s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
#
#         s3.upload_file(WAVE_OUTPUT_FILENAME, BUCKET_NAME, WAVE_OUTPUT_FILENAME)
#
#         # Transcribe
#
#         job_name = "test_transcribe" + str(datetime.datetime.now())[-6:]
#         job_uri = "s3://" + BUCKET_NAME + "/" + WAVE_OUTPUT_FILENAME
#
#         transcribe = boto3.client('transcribe', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY,
#                                   region_name="ap-northeast-2")
#         transcribe.start_transcription_job(
#             TranscriptionJobName=job_name,
#             Media={'MediaFileUri': job_uri},
#             MediaFormat='wav',
#             MediaSampleRateHertz=RATE,
#             LanguageCode='ko-KR'
#         )
#
#         elapsed_time = 0
#         while True:
#             status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
#             if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
#                 break
#
#             if elapsed_time == 0:
#                 print("Transcription start...")
#             else:
#                 print("Not ready yet. " + str(elapsed_time) + "sec passed.")
#
#             time.sleep(5)
#             elapsed_time += 5
#
#         print(status)
#
#         # Transcript Result File
#
#         transcript_file_uri = status["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
#         print(transcript_file_uri)
#         result = ""
#
#         with urllib.request.urlopen(transcript_file_uri) as url:
#             tr_json = json.loads(url.read().decode())
#             tr_list = tr_json['results']['transcripts']
#
#             for tr_item in tr_list:
#                 print(tr_item['transcript'])
#                 result += tr_item['transcript']
#
#         # wordcloud
#         font_path = 'SDSwaggerTTF.ttf'
#         wordcloud = WordCloud(font_path=font_path, width=1200, height=1200,
#                               background_color='black').generate(result)
#
#         plt.figure(figsize=(12, 12), facecolor='k')
#         plt.imshow(wordcloud)
#         plt.axis("off")
#         plt.tight_layout(pad=0)
#
#         # plt.show()
#         plt.savefig('wordcloud_without_axisoff2.png', facecolor='k', bbox_inches='tight')
#
#         self.signalExample.emit()



class UIWindow(QWidget):
    def __init__(self, parent=None):
        super(UIWindow, self).__init__(parent)
        self.background()

        self.button()
        self.resize(QSize(1920, 1080))

        self.background_music()

    def background_music(self):
        pygame.init()
        pygame.mixer.music.load("Josefina.mp3")
        pygame.mixer.music.play(-1)  # -1이면 무한반복


    def create_menu_window(self):
        pygame.quit()
        self.menu = main_window_.Menu()
        self.menu.show()

    def create_menu_window2(self):
        pygame.quit()
        self.menu2 = main_window_2.Menu2()
        self.menu2.show()

    def create_eyetraking_window(self):
        pygame.quit()
        self.eye = eyetracking.Eye()
        self.eye.reset = 0
        self.eye.show()

    def create_info_window(self):
        pygame.quit()
        self.information = aaaa.InfoWindow()
        self.information.show()

    def create_gift_window(self):
        pygame.quit()
        self.gift = box.BoxWindow()
        self.gift.show()

    def grafana(self):
        self.gra = graph.GGG()
        self.gra.show()


    def button(self):
        self.btn3 = PicButton(QPixmap('btn_시선교육.png'), self)
        self.btn3.resize(234, 225)
        self.btn3.move(360, 380)#(230, 380)
        eff1 = QGraphicsDropShadowEffect()
        self.btn3.setGraphicsEffect(eff1)
        self.btn3.clicked.connect(self.create_eyetraking_window)

        self.btn2 = PicButton(QPixmap('btn_기초감정교육.png'), self)######A를 10번정도 받으면? 이제 심화학습으로 가보세요.
        self.btn2.resize(234, 225)
        self.btn2.move(605, 380)#(475, 380)
        eff = QGraphicsDropShadowEffect()
        self.btn2.setGraphicsEffect(eff)
        self.btn2.clicked.connect(self.create_menu_window)

        self.btn2_ = PicButton(QPixmap('btn_심화감정교육.png'), self)
        self.btn2_.resize(234, 225)
        self.btn2_.move(850, 380)#(720, 380)
        eff0 = QGraphicsDropShadowEffect()
        self.btn2_.setGraphicsEffect(eff0)
        self.btn2_.clicked.connect(self.create_menu_window2)

        self.btn4 = PicButton(QPixmap('btn_학습그래프.png'), self)
        self.btn4.resize(234, 225)
        self.btn4.move(1095, 380)#(965, 380)
        eff2 = QGraphicsDropShadowEffect()
        self.btn4.setGraphicsEffect(eff2)
        self.btn4.clicked.connect(self.grafana)

        self.gg = PicButton(QPixmap('btn_보물상자.png'), self)
        self.gg.resize(234, 225)
        self.gg.move(1340, 380)#(1210, 380)
        effect = QGraphicsDropShadowEffect()
        self.gg.setGraphicsEffect(effect)
        self.gg.clicked.connect(self.create_gift_window)

        # self.btn = PicButton(QPixmap('btn_종료하기.png'), self)
        # self.btn.resize(234, 225)
        # self.btn.move(1455, 380)
        # eff3 = QGraphicsDropShadowEffect()
        # self.btn.setGraphicsEffect(eff3)
        # self.btn.clicked.connect(QCoreApplication.instance().quit)

        self.btn1 = PicButton(QPixmap('info_.png'), self) #도움말
        self.btn1.resize(60, 60)
        self.btn1.move(25, 20)
        eff4 = QGraphicsDropShadowEffect(blurRadius=5, xOffset=3, yOffset=3)
        self.btn1.setGraphicsEffect(eff4)
        self.btn1.clicked.connect(self.create_info_window)

        self.btn5 = PicButton(QPixmap('music.png'), self)  # 음악재생
        self.btn5.resize(60, 60)
        self.btn5.move(100, 20)
        eff5 = QGraphicsDropShadowEffect(blurRadius=5, xOffset=3, yOffset=3)
        self.btn5.setGraphicsEffect(eff5)
        self.btn5.clicked.connect(self.background_music)


    def background(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.lbl1 = QLabel(self)
        self.lbl1.setStyleSheet("border-image:url(__pineapple.png);")
        self.lbl1.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.lbl1)


class Main(QMainWindow):

    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        self.setGeometry(0, 30, 1920, 1080)
        self.setFixedSize(1920, 1080)
        self.startUIWindow()

    #     self.worker = Voice_record()
    #     self.worker_thread = QThread()
    #     self.worker.moveToThread(self.worker_thread)
    #     self.worker.signalExample.connect(self.signalMethodExample)
    #     self.worker_thread.start()
    #     self.VoiceTimer = QTimer()
    #     self.VoiceTimer.start()
    #     self.VoiceTimer.timeout.connect(self.worker.voice)
    #
    # def signalMethodExample(self):
    #     self.VoiceTimer.stop()
    #     self.worker_thread.terminate()



    def startUIWindow(self):
        self.Window = UIWindow(self)
        self.setWindowTitle('파인 홈스쿨')
        self.setWindowIcon(QIcon('mainlogo.png'))
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Main()
    sys.exit(app.exec_())