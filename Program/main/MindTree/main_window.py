import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore, QtGui, QtWidgets
import cv2
from ui_main_window import *
import pymysql
from multiprocessing import Queue
import boto3
from time import sleep
from playsound import playsound
from PIL import Image, ImageDraw, ExifTags, ImageColor
import io

class GIFLabel(QLabel):
    def __init__(self, gif, *args, **kwargs):
        QLabel.__init__(self, *args, **kwargs)

        movie = QMovie(gif)
        self.setMovie(movie)
        movie.start()

connection = pymysql.connect(host='203.252.208.222', user='root', password='MindTree@12345', db='imageupload', port=8008)
try:
    with connection.cursor() as cursor:  # 부모님 감정 name
        sql = "select name from images ORDER BY id DESC limit 1"
        cursor.execute(sql)
        emotionname = cursor.fetchone()
        # print("emotionname : ", emotionname[0])

    with connection.cursor() as cursor:  # 부모님 감정 value
        sql = "select emotion_value from images ORDER BY id DESC limit 1"
        cursor.execute(sql)
        emotionvalue = cursor.fetchone()
        # print("emotionvalue : ", emotionvalue[0])

    with connection.cursor() as cursor:  # 부모님 감정 id
        sql = "select id from images ORDER BY id DESC limit 1"
        cursor.execute(sql)
        img_id = cursor.fetchone()
        # print("img_id : ", img_id[0])
finally:
    connection.close()

connection_c = pymysql.connect(host='203.252.208.222', user='root', password='MindTree@12345', db='box_schema', port=8008)
try:
    with connection_c.cursor() as cursor:
        sql = "select value from pickup_box ORDER BY time DESC limit 1"
        cursor.execute(sql)
        coins = cursor.fetchone()
finally:
    connection_c.close()

BUF_SIZE = 30000
imageQ = Queue(BUF_SIZE)
emotionQ = Queue(BUF_SIZE)
feedbackQ = Queue(BUF_SIZE)
abcList = []

global count
count = 0

class getEmotion(QObject):
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

    # 백그라운드에서 돌아갈 함수 class
    def info_view(self):
        count = 0

        client = boto3.client('rekognition')

        global imagess
        if not imageQ.empty():
            imagess = imageQ.get()

            _, img_encoded = cv2.imencode('.jpg', imagess)

            rekresp = client.detect_faces(Image={'Bytes': img_encoded.tostring()}, Attributes=['ALL'])

            # print(rekresp['FaceDetails'])

            emo = ""
            for facedeets in rekresp['FaceDetails']:
                for emotiondeets in facedeets['Emotions']:

                    # if emotiondeets['Type'] == 'HAPPY':
                    #     print('해피 감정 수치 : ', emotiondeets['Confidence'])

                    if emotiondeets['Type'] == 'HAPPY':
                        emo = 'happy'
                    elif emotiondeets['Type'] == 'SAD':
                        emo = 'sad'
                    elif emotiondeets['Type'] == 'SURPRISED':
                        emo = 'surprise'
                    elif emotiondeets['Type'] == 'ANGRY':
                        emo = 'angry'
                    else:
                        emo = ''
                    if emo == emotionname[0] and emo != '':  # 아이가 부모사진을 보고 얼마나 감정을 잘 따라했는가?
                        # print('부모가 선택한 감정 : ', emotionname[0], ', 아이의 감정 수치 : ', emotiondeets['Confidence'])

                        emotionQ.put(emotiondeets['Confidence'])
                        feedbackQ.put(emotiondeets['Confidence'])
                        abcList.append(emotiondeets['Confidence'])


class sendDB(QObject):
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

    # 백그라운드에서 돌아갈 함수 class
    def insert_info_db(self):
        count1 = 0
        while (not emotionQ.empty()):
            emotion_v_ = emotionQ.get()

            # webcam_emotion_schema에 올리기.
            if connection.open:
                connection.close()

            else:
                connection2 = pymysql.connect(host='203.252.208.222', user='root', password='MindTree@12345',
                                              db='webcam_emotion_schema', port=8008)

                if count1 < 20000:
                    with connection2.cursor() as cursor:

                        sql = 'INSERT INTO webcam_emotion_value (id, img_id, img_emotion_name, img_emotion_value, webcam_emotion_value ) VALUES ( %s, %s, %s, %s, %s )'
                        cursor.execute(sql, (
                        count, img_id[0], emotionname[0], emotionvalue[0], emotion_v_))  # emotiondeets['Confidence']

                    connection2.commit()

                else:
                    connection2.close()


class e_FeedBack(QObject):
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

    def emotion_feed(self):
        while (not feedbackQ.empty()):
            feed_emotion = feedbackQ.get()

            # 피드백
            if feed_emotion < (emotionvalue[0]/2): #부모감정의 50% 이하로 따라했을때

                print("부모님감정", (emotionvalue[0]/2))
                print("feedbackQ", feed_emotion, "\n")

                if emotionname[0] == "happy":
                    playsound('speech_happy.mp3')
                    sleep(3)

                elif emotionname[0] == "sad":
                    playsound('speech_sad.mp3')
                    sleep(3)

                elif emotionname[0] == "surprise":
                    playsound('speech_surprise.mp3')
                    sleep(3)

                elif emotionname[0] == "angry":
                    playsound('speech_angry.mp3')
                    sleep(3)


endqueue = Queue(BUF_SIZE)
class EmotionWindow(QWidget):
    flag = 0

    def __init__(self):
        super().__init__()
        # playsound('emo_follow_voice.mp3')
        self.count = 0
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.timerview()
############################################################################################################
        self.worker = getEmotion()  # 백그라운드에서 돌아갈 인스턴스 소환
        self.worker_thread = QThread()  # 따로 돌아갈 thread를 하나 생성
        self.worker.moveToThread(self.worker_thread)  # worker를 만들어둔 쓰레드에 넣어줍니다
        self.worker_thread.start()  # 쓰레드를 실행합니다.
        self.tt = QTimer()  ##add
        self.tt.start()  ##add
        self.tt.timeout.connect(self.worker.info_view)  ##add

        self.worker2 = sendDB()  # 백그라운드에서 돌아갈 인스턴스 소환
        self.worker_thread2 = QThread()  # 따로 돌아갈 thread를 하나 생성
        self.worker2.moveToThread(self.worker_thread2)  # worker를 만들어둔 쓰레드에 넣어줍니다
        self.worker_thread2.start()  # 쓰레드를 실행합니다.
        self.tt2 = QTimer()  ##add
        self.tt2.start()  ##add
        self.tt2.timeout.connect(self.worker2.insert_info_db)  ##add

        self.worker3 = e_FeedBack()  # 백그라운드에서 돌아갈 인스턴스 소환
        self.worker_thread3 = QThread()  # 따로 돌아갈 thread를 하나 생성
        self.worker3.moveToThread(self.worker_thread3)  # worker를 만들어둔 쓰레드에 넣어줍니다
        self.worker_thread3.start()  # 쓰레드를 실행합니다.
        self.tt3 = QTimer()  ##add
        self.tt3.start()  ##add
        self.tt3.timeout.connect(self.worker3.emotion_feed)  ##add
############################################################################################################
        endqueue.put(1)

        self.follow = QLabel(self)
        self.follow.setText("        내 표정을 따라해봐")
        self.follow.move(0, 100)
        self.follow.resize(620, 100)
        self.follow.setStyleSheet('font-size: 60pt; font-family: 스웨거 TTF; color: white;')
        self.follow.show()

        self.step = QLabel(self)
        self.step.setStyleSheet("border-image:url(단계.png);")
        self.step.move(0, 900)
        self.step.resize(760, 70)
        self.step.show()

        self.fontTimer = QTimer()  # 수치 뜨는 판별
        self.fontTimer.start()
        self.fontTimer.timeout.connect(self.ffinish0)

        self.mainTimer1 = QTimer() # 첫번째 판별
        self.mainTimer1.start(3000)# 3초 뒤
        self.mainTimer1.timeout.connect(self.ffinish1)

        self.mainTimer2 = QTimer() # 두번째 판별
        self.mainTimer2.start(6000)# 6초 뒤
        self.mainTimer2.timeout.connect(self.ffinish2)

        self.mainTimer3 = QTimer() # 세번째 판별
        self.mainTimer3.start(9000)# 9초 뒤
        self.mainTimer3.timeout.connect(self.ffinish3)

        self.mainTimer = QTimer()  # 최종 판별
        self.mainTimer.start(11000)  # 11초 동안 감정 학습 중 #11초 뒤에 실행해서 닫는다!!!!
        self.mainTimer.timeout.connect(self.ffinish)

    def ffinish0(self):
        a = 0

        try:
            a = sum(abcList) / len(abcList)
        except ZeroDivisionError:
            a = 0
            # print("ZeroDivision")

        self.fi = QLabel(self)
        self.fi.setText(str(round(a,2)))
        self.fi.move(620, 100)
        self.fi.resize(170, 100)
        self.fi.setStyleSheet('font-size: 45pt; font-family: 스웨거 TTF;')
        self.fi.show()


    def ffinish1(self):
        self.mainTimer1.stop()
        a = 0

        try:
            a = sum(abcList) / len(abcList)
        except ZeroDivisionError:
            a = 0
            # print("ZeroDivision")


        if a > emotionvalue[0]-30 :
            self.frame = QLabel(self)
            self.frame.setStyleSheet("border-image:url(팝업창A.png);")
            self.frame.resize(150, 150)
            self.frame.move(30, 930)
            self.frame.show()

        elif a > emotionvalue[0]-50 :
            self.frame = QLabel(self)
            self.frame.setStyleSheet("border-image:url(팝업창B.png);")
            self.frame.resize(150, 150)
            self.frame.move(30, 930)
            self.frame.show()

        else:
            self.frame = QLabel(self)
            self.frame.setStyleSheet("border-image:url(팝업창C.png);")
            self.frame.resize(150, 150)
            self.frame.move(30, 930)
            self.frame.show()

    def ffinish2(self):
        self.mainTimer2.stop()
        a = 0

        try:
            a = sum(abcList) / len(abcList)
        except ZeroDivisionError:
            a = 0
            # print("ZeroDivision")


        if a > emotionvalue[0]-30 :
            self.frame = QLabel(self)
            self.frame.setStyleSheet("border-image:url(팝업창A.png);")
            self.frame.resize(150, 150)
            self.frame.move(300, 930)
            self.frame.show()

        elif a > emotionvalue[0]-50 :
            self.frame = QLabel(self)
            self.frame.setStyleSheet("border-image:url(팝업창B.png);")
            self.frame.resize(150, 150)
            self.frame.move(300, 930)
            self.frame.show()

        else:
            self.frame = QLabel(self)
            self.frame.setStyleSheet("border-image:url(팝업창C.png);")
            self.frame.resize(150, 150)
            self.frame.move(300, 930)
            self.frame.show()

    def ffinish3(self):
        self.mainTimer3.stop()
        a = 0

        try:
            a = sum(abcList) / len(abcList)
        except ZeroDivisionError:
            a = 0
            # print("ZeroDivision")


        if a > emotionvalue[0]-30 :
            self.frame = QLabel(self)
            self.frame.setStyleSheet("border-image:url(팝업창A.png);")
            self.frame.resize(150, 150)
            self.frame.move(580, 930)
            self.frame.show()

        elif a > emotionvalue[0]-50 :
            self.frame = QLabel(self)
            self.frame.setStyleSheet("border-image:url(팝업창B.png);")
            self.frame.resize(150, 150)
            self.frame.move(580, 930)
            self.frame.show()

        else:
            self.frame = QLabel(self)
            self.frame.setStyleSheet("border-image:url(팝업창C.png);")
            self.frame.resize(150, 150)
            self.frame.move(580, 930)
            self.frame.show()



    def sound_very_good(self):
        playsound('speech_very good.mp3')
        self.stimer1.stop()
        self.stimer1.deleteLater()

    def sound_good(self):
        playsound('speech_good.mp3')
        self.stimer2.stop()
        self.stimer2.deleteLater()

    def sound_next_time(self):
        playsound('speech_next_time.mp3')
        self.stimer3.stop()
        self.stimer3.deleteLater()


    def A_showMessageBox(self):
        a = QPixmap("팝업창A.png")
        a = a.scaled(300, 300)

        msg = QMessageBox()
        msg.setWindowTitle("최종 평가")
        msg.setStyleSheet("background-color: rgb(255, 204, 103);")
        msg.setWindowIcon(QIcon("mainlogo.png"))

        msg.setIcon(QMessageBox.Information)
        msg.setIconPixmap(a)  # 옆에 뜨는 이미지!!!

        msg.setStandardButtons(QMessageBox.Ok)
        buttonOK = msg.button(QMessageBox.Ok)
        buttonOK.setStyleSheet("background-color: rgb(255, 255, 255);")
        buttonOK.setText('학습종료하기')

        self.stimer1 = QTimer()
        self.stimer1.start(1000)#1초
        self.stimer1.timeout.connect(self.sound_very_good)
        msg.buttonClicked.connect(self.Star_showMessageBox_a) # 보상체계

        # endqueue.put(0)
        msg.exec_()


    def B_showMessageBox(self):
        b = QPixmap("팝업창B.png")
        b = b.scaled(300, 300)

        msg2 = QMessageBox()
        msg2.setWindowTitle("최종 평가")
        msg2.setStyleSheet("background-color: rgb(255, 204, 103);")
        msg2.setWindowIcon(QIcon("mainlogo.png"))

        msg2.setIcon(QMessageBox.Information)
        msg2.setIconPixmap(b)  # 옆에 뜨는 이미지!!!

        msg2.setStandardButtons(QMessageBox.Ok)
        buttonOK = msg2.button(QMessageBox.Ok)
        buttonOK.setStyleSheet("background-color: rgb(255, 255, 255);")
        buttonOK.setText('학습종료하기')

        self.stimer2 = QTimer()
        self.stimer2.start(1000)#1초
        self.stimer2.timeout.connect(self.sound_good)
        msg2.buttonClicked.connect(self.Star_showMessageBox_b) # 보상체계

        # endqueue.put(0)
        msg2.exec_()

    def C_showMessageBox(self):
        c = QPixmap("팝업창C.png")
        c = c.scaled(300, 300)

        msg3 = QMessageBox()
        msg3.setWindowTitle("최종 평가")
        msg3.setStyleSheet("background-color: rgb(255, 204, 103);")
        msg3.setWindowIcon(QIcon("mainlogo.png"))

        msg3.setIcon(QMessageBox.Information)
        msg3.setIconPixmap(c)  # 옆에 뜨는 이미지!!!

        msg3.setStandardButtons(QMessageBox.Ok)
        buttonOK = msg3.button(QMessageBox.Ok)
        buttonOK.setStyleSheet("background-color: rgb(255, 255, 255);")
        buttonOK.setText('학습종료하기')

        self.stimer3 = QTimer()
        self.stimer3.start(1000)#1초
        self.stimer3.timeout.connect(self.sound_next_time)
        msg3.buttonClicked.connect(self.Star_showMessageBox_c) # 보상체계

        # endqueue.put(0)
        msg3.exec_()


    def Star_showMessageBox_a(self):
        msg = QMessageBox()
        msg.setWindowTitle("보상")
        msg.setStyleSheet("background-color: rgb(253, 225, 120);")
        msg.setWindowIcon(QIcon("mainlogo.png"))

        msg.setIcon(QMessageBox.Information)
        msg.setIconPixmap(QPixmap("treasure_box100.gif").scaledToWidth(100))
        icon_label = msg.findChild(QLabel, "qt_msgboxex_icon_label")
        star = QMovie("treasure_box100.gif")
        icon_label.setMovie(star)
        star.start()

        msg.setStandardButtons(QMessageBox.Ok)
        buttonOK = msg.button(QMessageBox.Ok)
        buttonOK.setStyleSheet("background-color: rgb(255, 255, 255);")
        buttonOK.setText('보물상자 획득!')

        connection6 = pymysql.connect(host='203.252.208.222', user='root', password='MindTree@12345',
                                      db='box_schema', port=8008)
        with connection6.cursor() as cursor:
            sql = 'INSERT INTO pickup_box (value) VALUES ( %s )'
            cursor.execute(sql, (coins[0]+100))
            connection6.commit()
            connection6.close()

        # endqueue.put(0)
        msg.exec_()

    def Star_showMessageBox_b(self):
        msg = QMessageBox()
        msg.setWindowTitle("보상")
        msg.setStyleSheet("background-color: rgb(253, 225, 120);")
        msg.setWindowIcon(QIcon("mainlogo.png"))

        msg.setIcon(QMessageBox.Information)
        msg.setIconPixmap(QPixmap("treasure_box50.gif").scaledToWidth(100))
        icon_label = msg.findChild(QLabel, "qt_msgboxex_icon_label")
        star = QMovie("treasure_box50.gif")
        icon_label.setMovie(star)
        star.start()

        msg.setStandardButtons(QMessageBox.Ok)
        buttonOK = msg.button(QMessageBox.Ok)
        buttonOK.setStyleSheet("background-color: rgb(255, 255, 255);")
        buttonOK.setText('보물상자 획득!')
        # buttonOK.resize(500,100)

        connection7 = pymysql.connect(host='203.252.208.222', user='root', password='MindTree@12345',
                                      db='box_schema', port=8008)
        with connection7.cursor() as cursor:
            sql = 'INSERT INTO pickup_box (value) VALUES ( %s )'
            cursor.execute(sql, (coins[0]+50))
            connection7.commit()
            connection7.close()

        # endqueue.put(0)
        msg.exec_()

    def Star_showMessageBox_c(self):
        msg = QMessageBox()
        msg.setWindowTitle("보상")
        msg.setStyleSheet("background-color: rgb(253, 225, 120);")
        msg.setWindowIcon(QIcon("mainlogo.png"))

        msg.setIcon(QMessageBox.Information)
        msg.setIconPixmap(QPixmap("treasure_box30.gif").scaledToWidth(100))
        icon_label = msg.findChild(QLabel, "qt_msgboxex_icon_label")
        star = QMovie("treasure_box30.gif")
        icon_label.setMovie(star)
        star.start()

        msg.setStandardButtons(QMessageBox.Ok)
        buttonOK = msg.button(QMessageBox.Ok)
        buttonOK.setStyleSheet("background-color: rgb(255, 255, 255);")
        buttonOK.setText('보물상자 획득!')
        # buttonOK.resize(500,100)

        connection8 = pymysql.connect(host='203.252.208.222', user='root', password='MindTree@12345',
                                      db='box_schema', port=8008)
        with connection8.cursor() as cursor:
            sql = 'INSERT INTO pickup_box (value) VALUES ( %s )'
            cursor.execute(sql, (coins[0]+30))
            connection8.commit()
            connection8.close()

        # endqueue.put(0)
        msg.exec_()

    def ffinish(self):
        self.close() #웹캠 닫는 코드
        self.worker_thread.terminate()
        self.worker_thread2.terminate()
        self.worker_thread3.terminate()
        self.fontTimer.stop()
        self.cap.release()

        EmotionWindow.flag = 1

        emotionSum = sum(abcList)
        average = emotionSum / len(abcList)
        # print("$$$$$", "emotionSum : ", emotionSum, ", len(abcList) : ", len(abcList), ", average : ", average)

        if emotionname[0] == "happy":
            emott = 1

        elif emotionname[0] == "sad":
            emott = 2

        elif emotionname[0] == "angry":
            emott = 3

        elif emotionname[0] == "surprise":
            emott = 4

        connection3 = pymysql.connect(host='203.252.208.222', user='root', password='MindTree@12345', db='emotion_sum', port=8008)
        with connection3.cursor() as cursor:
            sql2 = 'INSERT INTO emotion_sum (plus, emot) VALUES ( %s, %s )'
            cursor.execute(sql2, (average, emott))
            connection3.commit()
            connection3.close()

        if endqueue.get() == 1:
            if (average > emotionvalue[0]-30) :
                print("부모감정1", emotionvalue[0]  - 30, ", 아이평균감정1 : ", average)
                self.A_showMessageBox()

            elif (average > emotionvalue[0]-50) :
                print("부모감정1", emotionvalue[0] - 50, ", 아이평균감정1 : ", average)
                self.B_showMessageBox()

            else :
                print("아이평균감정 : ", average)
                self.C_showMessageBox()

        self.mainTimer.stop()


    def timerview(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.viewCam)
        self.controlTimer()

    def controlTimer(self):
        print("in control")
        self.cap = cv2.VideoCapture(0)
        self.timer.start(20)

    def viewCam(self):
        self.count = self.count + 1
        if (self.cap.isOpened()):
            ret, image = self.cap.read()
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            height, width, channel = image.shape
            step = channel * width
            qImg = QImage(image.data, width, height, step, QImage.Format_RGB888)
            qImg = qImg.scaled(750, 850)  # 웹캠 사이즈 조절
            self.ui.image_label.setPixmap(QPixmap.fromImage(qImg))  # 웹캠 창 띄워주는 부분

            if (not imageQ.full()) and (self.count % 30 == 0):  # 1초마다 이미지 넣는 코드
                imageQ.put(image)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    emotionWindow = EmotionWindow()
    emotionWindow.show()

    sys.exit(app.exec_())