import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from main_window2 import *
import main_window2
from ui_main_window import *
import cv2
import urllib.request
import pymysql
import pygame
from playsound import playsound
from time import sleep

# 제일 최근 이미지를 가져오기 위한 코드 #
connection = pymysql.connect(host='203.252.208.222', user='root', password='MindTree@12345', db='imageupload',port=8008)
abcQQ = Queue()

try:
    with connection.cursor() as cursor:  # 최신사진
        sql = "select url from images ORDER BY id DESC limit 1"
        cursor.execute(sql)
        result = cursor.fetchone()
        # print(result[0])

    with connection.cursor() as cursor:  # 부모님 감정 name
        sql = "select name from images ORDER BY id DESC limit 1"
        cursor.execute(sql)
        emotionname = cursor.fetchone()
        # print(emotionname[0])

    with connection.cursor() as cursor:  # 부모님 감정 value
        sql = "select emotion_value from images ORDER BY id DESC limit 1"
        cursor.execute(sql)
        emotionvalue = cursor.fetchone()
        # print(emotionvalue[0])

    with connection.cursor() as cursor:  # 부모님 감정 id
        sql = "select id from images ORDER BY id DESC limit 1"
        cursor.execute(sql)
        img_id = cursor.fetchone()
        # print(img_id[0])

finally:
    connection.close()


# 최신 emotion_sum을 가져오기 위한 코드 #
e_connection = pymysql.connect(host='203.252.208.222', user='root', password='MindTree@12345', db='emotion_sum', port=8008)
try:
    with e_connection.cursor() as cursor:  # emotion_sum
        sql = "select plus from emotion_sum ORDER BY timestamp DESC limit 1"
        cursor.execute(sql)
        emo_sum = cursor.fetchone()
        # print("emo_sum", emo_sum[0])
finally:
    e_connection.close()


class PicButton(QAbstractButton):
    def __init__(self, pixmap, parent=None):
        super(PicButton, self).__init__(parent)
        self.pixmap = pixmap

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

    def sizeHint(self):
        return self.pixmap.size()


class Menu2(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setGeometry(0, 0, 1920, 1080)
        self.setFixedSize(1920, 1080)

        self.setWindowTitle("파인 홈스쿨")
        self.setWindowIcon(QIcon('mainlogo.png'))

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        self.lay = QHBoxLayout(self.main_widget)
        self.lay.setContentsMargins(0, 0, 120, 0)
        self.lay.setAlignment(Qt.AlignRight)

        self.setStyleSheet("background-color: #d0db27;") # 배경색

        self.frame = QLabel(self)
        self.frame.setStyleSheet("border-image:url(파인애플2r.png);")
        self.frame.resize(960, 1080)
        self.frame.move(0,0)
        self.frame.show()

        self.frame1 = QLabel(self)
        self.frame1.setStyleSheet("border-image:url(파인애플2.png);")
        self.frame1.resize(960, 100)
        self.frame1.move(960, 0)
        self.frame1.show()



        # 부모님 사진 (감정 학습할 사진)
        self.parent = QLabel(self)
        self.parent.move(135,115) # 부모사진 위치이동
        self.parent.resize(750,850) # 부모사진 사이즈조절
        image_url = result[0]  # 서버에서 젤 최근에 있는 사진 가져오기
        parent_image = urllib.request.urlopen(image_url).read()
        pixmap = QPixmap()
        pixmap.loadFromData(parent_image)
        pixmap = pixmap.scaled(750, 850)
        self.parent.setPixmap(pixmap)

        self.question()
        self.soundtimer = QTimer()
        self.soundtimer.start(1000)
        self.soundtimer.timeout.connect(self.sound_what_kind_of_emotion)
        self.show()

    def sound_what_kind_of_emotion(self):
        playsound('emo_quiz_voice.mp3')
        self.soundtimer.stop()
        self.soundtimer.deleteLater()

    def show_webcam(self): # 웹캠보이기
        self.cam2 = EmotionWindow2()
        self.lay.addWidget(self.cam2)


    def question(self):
        self.q = PicButton(QPixmap('question.png'), self)
        self.q.resize(750, 270)
        self.q.move(1050, 65)

        self.btn2 = PicButton(QPixmap('pine_angry.png'), self)
        self.btn2.resize(250, 250)
        self.btn2.move(1100, 400)
        self.btn2.clicked.connect(self.trueorfalse_angry)

        self.btn3 = PicButton(QPixmap('pine_happy.png'), self)
        self.btn3.resize(250, 250)
        self.btn3.move(1450, 400)
        self.btn3.clicked.connect(self.trueorfalse_happy)

        self.btn4 = PicButton(QPixmap('pine_sad.png'), self)
        self.btn4.resize(250, 250)
        self.btn4.move(1100, 700)
        self.btn4.clicked.connect(self.trueorfalse_sad)

        self.btn = PicButton(QPixmap('pine_surprise.png'), self)
        self.btn.resize(250, 250)
        self.btn.move(1450, 700)
        self.btn.clicked.connect(self.trueorfalse_surprise)

        self.btn5 = PicButton(QPixmap('뒤로가기_pink.png'), self)
        self.btn5.resize(80, 80)
        self.btn5.move(20, 980)
        self.btn5.clicked.connect(self.close)


############################################################################################팝업창
    def good_showMessageBox(self):
        good = QPixmap("팝업_정답.png")
        good = good.scaled(300,300)

        msg = QMessageBox()
        msg.setWindowTitle("정답확인")
        msg.setStyleSheet("background-color: rgb(255, 204, 103);")
        msg.setWindowIcon(QIcon("mainlogo.png"))

        msg.setIcon(QMessageBox.Information)
        msg.setIconPixmap(good)  # 옆에 뜨는 이미지!!!

        msg.setStandardButtons(QMessageBox.Ok)
        buttonOK = msg.button(QMessageBox.Ok)
        buttonOK.setStyleSheet("background-color: rgb(255, 255, 255);")
        buttonOK.setText('시작')

        msg.buttonClicked.connect(self.show_webcam)
        msg.exec_()

    def bad_showMessageBox(self):
        bad = QPixmap("팝업_오답.png")#여기에 못했어요 이미지
        bad = bad.scaled(300, 300)

        msg = QMessageBox()
        msg.setWindowTitle("정답확인")
        msg.setStyleSheet("background-color: rgb(255, 204, 103);")
        msg.setWindowIcon(QIcon("mainlogo.png"))

        msg.setIcon(QMessageBox.Information)
        msg.setIconPixmap(bad)  # 옆에 뜨는 이미지!!!

        msg.setStandardButtons(QMessageBox.Ok)
        buttonOK = msg.button(QMessageBox.Ok)
        buttonOK.setStyleSheet("background-color: rgb(255, 255, 255);")
        buttonOK.setText('시작')

        msg.buttonClicked.connect(self.show_webcam)
        msg.exec_()
################################################################################################
    '''
안드로이드안에서 정의해놓은것 : happy, angry, sad, surprised
    '''
    def trueorfalse_angry(self):
        self.q.close()
        self.btn2.close()
        self.btn3.close()
        self.btn4.close()
        self.btn.close()

        if emotionname[0] == "angry": #anger
            self.good_showMessageBox()
        else:
            self.bad_showMessageBox()

    def trueorfalse_happy(self):
        self.q.close()
        self.btn2.close()
        self.btn3.close()
        self.btn4.close()
        self.btn.close()

        if emotionname[0] == "happy": #happiness
            self.good_showMessageBox()
        else:
            self.bad_showMessageBox()

    def trueorfalse_sad(self):
        self.q.close()
        self.btn2.close()
        self.btn3.close()
        self.btn4.close()
        self.btn.close()

        if emotionname[0] == "sad": #sadness
            self.good_showMessageBox()
        else:
            self.bad_showMessageBox()

    def trueorfalse_surprise(self):
        self.q.close()
        self.btn2.close()
        self.btn3.close()
        self.btn4.close()
        self.btn.close()

        if emotionname[0] == "surprise":#surprise
            self.good_showMessageBox()
        else:
            self.bad_showMessageBox()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex2 = Menu2()
    sys.exit(app.exec_())