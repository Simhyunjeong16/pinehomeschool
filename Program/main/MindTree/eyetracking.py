import urllib.request
import pymysql
import threading
import time
from peyetribe import EyeTribe
from PyQt5.QtCore import Qt,QTimer
from PyQt5.QtGui import QPainter, QPixmap, QIcon, QMovie
from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel, QAbstractButton, QWidget, QMessageBox, QHBoxLayout, QMainWindow, QApplication
from multiprocessing import Queue
import winsound
import requests
import json
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
font_path = 'SDSwaggerTTF.ttf'
fontprop = fm.FontProperties(fname=font_path, size=18)

# child_eye_data = pd.DataFrame(columns=['x', 'y', 'eye_location'])
child_eye_data = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
points = list()
BUF_SIZE = 30000

###
box_q = Queue(BUF_SIZE)
glass_q = Queue(BUF_SIZE)

signal_good = Queue(BUF_SIZE)

xL = Queue(BUF_SIZE)
yL = Queue(BUF_SIZE)

x_goal = Queue(BUF_SIZE)
y_goal = Queue(BUF_SIZE)
p_move = Queue(BUF_SIZE)

x = Queue(BUF_SIZE)
y = Queue(BUF_SIZE)

Lsplt_x= Queue(BUF_SIZE)
Lsplt_y= Queue(BUF_SIZE)

# 제일 최근 이미지를 가져오기 위한 코드 #
connection = pymysql.connect(host='203.252.208.222', user='root', password='MindTree@12345', db='imageupload',port =8008)
connection_c = pymysql.connect(host='203.252.208.222', user='root', password='MindTree@12345', db='box_schema', port=8008)

try:
    with connection.cursor() as cursor:  # 최신사진
        sql = "select url from images ORDER BY id DESC limit 1"
        cursor.execute(sql)
        image_result = cursor.fetchone()

finally:
    connection.close()
try:
    with connection_c.cursor() as cursor:
        sql = "select value from pickup_box ORDER BY time DESC limit 1"
        cursor.execute(sql)
        coins = cursor.fetchone()
finally:
    connection_c.close()

class GIFLabel(QLabel):
    def __init__(self, gif, *args, **kwargs):
        QLabel.__init__(self, *args, **kwargs)

        movie = QMovie(gif)
        self.setMovie(movie)
        movie.start()
class PicButton(QAbstractButton):
    def __init__(self, pixmap, parent=None):
        super(PicButton, self).__init__(parent)
        self.pixmap = pixmap

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

    def sizeHint(self):
        return self.pixmap.size()

class Eye(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setGeometry(0, 0, 1920, 1080)
        self.setFixedSize(1920, 1080)

        self.setWindowTitle("파인 홈스쿨")
        self.setWindowIcon(QIcon('mainlogo.png'))

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.lay = QHBoxLayout(self.main_widget)
        self.lay.setContentsMargins(0, 0, 0, 0)

        # 배경
        self.lbl1 = QLabel(self)
        self.lbl1.setStyleSheet("border-image:url(pineapple2_eye.png);")
        self.lbl1.setAlignment(Qt.AlignCenter)
        self.lay.addWidget(self.lbl1)

        self.frames2 = QLabel(self)
        self.frames2.setStyleSheet("border-image:url(frames2.png);")
        self.frames2.resize(320, 150)
        self.frames2.move(780, 0)
        self.frames2.show()

        self.frames = QLabel(self)
        self.frames.setStyleSheet("border-image:url(frames_pink.png);")
        self.frames.resize(860, 950)
        self.frames.move(530, 65)
        self.frames.show()

        self.btn5 = PicButton(QPixmap('뒤로가기_pink.png'), self)
        self.btn5.resize(80, 80)
        self.btn5.move(20, 980)
        self.btn5.clicked.connect(self.back)

        # 부모님 사진 (감정 학습할 사진)
        self.parent = QLabel(self)
        image_url = image_result[0]  # 서버에서 젤 최근에 있는 사진 가져오기
        parent_image = urllib.request.urlopen(image_url).read()
        pixmap = QPixmap()
        pixmap.loadFromData(parent_image)
        self.parent.setPixmap(pixmap)

        self.parent.move(560, 90)  # (1920-800)/2, (1080-900)/2
        self.parent.setScaledContents(5)
        self.parent.resize(800, 900)#(1400, 1080)

        #안경 쓴 부모님
        self.glasses_parent = QLabel(self)
        image_url = image_result[0]  # 서버에서 젤 최근에 있는 사진 가져오기
        glasses_parent_image = urllib.request.urlopen(image_url).read()
        pixmap = QPixmap()
        pixmap.loadFromData(glasses_parent_image)
        self.glasses_parent.setPixmap(pixmap)

        self.glasses_parent.move(60, 65)  # (1920-800)/2, (1080-900)/2
        self.glasses_parent.setScaledContents(5)
        self.glasses_parent.resize(400, 450)#(1400, 1080)

        self.eyetitle = QLabel(self)
        pixmap = QPixmap("eyetitle.png")
        self.eyetitle.move(60,530)
        self.eyetitle.setScaledContents(10)
        self.eyetitle.resize(400,50)
        self.eyetitle.setPixmap(pixmap)
        self.show()

        self.reset = 0
        self.soundFlag = 0
        self.maincount = 0
        self.cnt = 0
        self.jumsu = 0

        tracker = Tracker()
        self._eye = threading.Thread(target=tracker.eye_thread, daemon=True) # daemon=True
        self._eye.start()
        self.Glass()
        self.sunglass_ui()
        self.feedback = threading.Thread(target=self.feedback_sound, daemon=True)  # daemon=True
        self.feedback.start()

    def back(self):
        self.close()
        self.soundFlag = 1
        self.reset = 1
        self.maincount = 1000
        winsound.PlaySound(None, winsound.SND_FILENAME)

    def success_showMessageBox(self):
        a = QPixmap("눈맞춤성공.png")
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
        msg.buttonClicked.connect(self.Star_showMessageBox_a) # 보상체계

        msg.exec_()


    def fail_showMessageBox(self):
        b = QPixmap("다음에도전.png")
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
        msg2.buttonClicked.connect(self.Star_showMessageBox_b) # 보상체계


        msg2.exec_()

    def Star_showMessageBox_a(self):#####################보상체계 메세지박스
        msg = QMessageBox()
        msg.setWindowTitle("보상")
        msg.setStyleSheet("background-color: rgb(253, 225, 120);")
        msg.setWindowIcon(QIcon("mainlogo.png"))

        msg.setIcon(QMessageBox.Information)
        msg.setIconPixmap(QPixmap("treasure_box100.gif").scaledToWidth(100))
        icon_label = msg.findChild(QLabel, "qt_msgboxex_icon_label")
        star = QMovie("treasure_box100.gif")
        icon_label.setMovie(별)
        star.start()

        msg.setStandardButtons(QMessageBox.Ok)
        buttonOK = msg.button(QMessageBox.Ok)
        buttonOK.setStyleSheet("background-color: rgb(255, 255, 255);")
        buttonOK.setText('보물상자 획득!')
        # buttonOK.resize(500,100)

        connection6 = pymysql.connect(host='203.252.208.222', user='root', password='MindTree@12345',
                                      db='box_schema', port=8008)
        with connection6.cursor() as cursor:
            sql = 'INSERT INTO pickup_box (value) VALUES ( %s )'
            cursor.execute(sql, (coins[0]+100))
            connection6.commit()
            connection6.close()

        msg.exec_()

    def Star_showMessageBox_b(self):#####################보상체계 메세지박스
        msg = QMessageBox()
        msg.setWindowTitle("보상")
        msg.setStyleSheet("background-color: rgb(253, 225, 120);")
        msg.setWindowIcon(QIcon("mainlogo.png"))

        msg.setIcon(QMessageBox.Information)
        msg.setIconPixmap(QPixmap("treasure_box50.gif").scaledToWidth(100))
        icon_label = msg.findChild(QLabel, "qt_msgboxex_icon_label")
        star = QMovie("treasure_box50.gif")
        icon_label.setMovie(별)
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

        msg.exec_()


    def Glass(self): #왼쪽에 안경쓴 사람

        glass_num = glass_q.get()
        sizeX = int(glass_num[0])
        sizeY = int(glass_num[1])
        moveX = int(glass_num[2])
        moveY = int(glass_num[3])


        self.glass = QLabel(self)  # 왼

        pixmap = QPixmap("sunglass.png")  # 왼
        self.glass.move(moveX-100 , moveY+30 )
        self.glass.setScaledContents(5)
        self.glass.resize(sizeX, sizeY)
        self.glass.setPixmap(pixmap)

        self.glass.show()

    def sunglass_ui(self): #선글라스

        box_num = box_q.get()
        sizeX = int(box_num[0])
        sizeY = int(box_num[1])


        self.pixel_glass = QLabel(self)  # 왼
        pixmap = QPixmap("sunglass.png")  # 왼
        self.pixel_glass.setScaledContents(10)
        self.pixel_glass.resize(sizeX, sizeY)

        self.pixel_glass.setPixmap(pixmap)
        print("sunglass")

        self.pixel = threading.Thread(target=self.sunglass_move, daemon=True)
        self.pixel.start()

    def sunglass_move(self):
        tracker = EyeTribe()
        tracker.connect()
        tracker.pushmode()

        box_num = box_q.get()
        sizeX = int(box_num[0])
        sizeY = int(box_num[1])
        moveX = int(box_num[2])
        moveY = int(box_num[3])

        print("reset",self.reset)
        if self.reset == 0:
            self.maincount = 0
            while self.maincount < 700:

                n = tracker.next()
                str_n = str(n)
                splt_n = str_n.split(';')

                splt_n[5] = float(splt_n[5]) #결합 x
                splt_n[6] = float(splt_n[6]) #결합 y

                splt_n[9] = int(splt_n[9])  # 왼x
                splt_n[10] = int(splt_n[10])  # 왼y

                if self.maincount % 5 == 0:

                    xL.put(splt_n[5])
                    yL.put(splt_n[6])

                    Lsplt_x.put(splt_n[9])
                    Lsplt_y.put(splt_n[10])

                if not xL.empty() and not yL.empty():
                    Lx = xL.get()
                    Ly = yL.get()

                    if Lx == 0.0 and Ly == 0.0:
                      self.pixel_glass.close()
                      self.pixel_glass.repaint() #다시 그려줌

                    else:
                        self.pixel_glass.show()
                        self.pixel_glass.move(Lx, Ly)
                        self.pixel_glass.update()
                if not Lsplt_x.empty() and not Lsplt_y.empty() :
                    cam_Lx=Lsplt_x.get()
                    cam_Ly=Lsplt_y.get()

                    if  moveX  <= cam_Lx and (moveX + 275) >= cam_Lx and moveY  <=cam_Ly and (moveY + 20)>=cam_Ly:
                        self.soundFlag = 1
                        self.good_sound()
                        self.pixel_glass.move(moveX + 265, moveY + 20)
                        self.pixel_glass.resize(sizeX + 30, sizeY + 20)
                        time.sleep(1)
                        self.maincount = 700
                        self.cnt = 1

                        break

                self.maincount += 1

            if self.maincount == 700:
                self.soundFlag = 1
                self.reset = 1
                winsound.PlaySound(None, winsound.SND_FILENAME)
                if self.cnt == 1:
                    self.jumsu=1 #성공
                    self.success_showMessageBox()
                else:
                    self.jumsu = 0  #실패
                    self.fail_showMessageBox()

                df = pd.DataFrame(child_eye_data)

                plt.pcolor(df)

                plt.xticks(np.arange(1, len(df.columns), 1), df.columns)
                plt.yticks(np.arange(1, len(df.index), 1), df.index)

                plt.xlabel('X', fontsize=14)
                plt.ylabel('Y', fontsize=14)

                mycmap = plt.cm.YlOrRd
                mycmap._init()
                mycmap._lut[:, -1] = np.linspace(0.8, 0.8, 255 + 4)
                image_url = image_result[0]
                img = plt.imread(urllib2.urlopen(image_url), format='jpeg')
                fig, ax = plt.subplots()
                ax.set_title('아이의 시선', fontproperties=fontprop, fontsize=20)
                ax.imshow(img, extent=[0, 10, 0, 10])
                ax.pcolor(df, cmap=plt.cm.YlOrRd)
                plt.savefig('1108.png')

                tracker.pullmode()
                tracker.close()

    def good_sound(self):

        winsound.PlaySound("ok.wav", winsound.SND_FILENAME)

    def feedback_sound(self):# 피드백 사운드 나오는 곳

        if self.reset == 0:
            count = 0
            try:
                while count < 700:
                        if self.soundFlag == 0:
                            time.sleep(2)
                            winsound.PlaySound("look_my_eyes.wav", winsound.SND_FILENAME)
            except EOFError:
                print('Why did you do an EOF on me?')

class Point2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Tracker(): #QWidget
    def __init__(self):
        self.data_count = 0

    def eye_thread(self):

        subscription_key = '24ca52a877b44258a1de47de06888a8a'
        assert subscription_key

        face_api_url = 'https://koreacentral.api.cognitive.microsoft.com/face/v1.0/detect'

        image_url = image_result[0]

        headers = {'Ocp-Apim-Subscription-Key': subscription_key}

        params = {
            'returnFaceLandmarks': 'true',
            'returnFaceAttributes': 'emotion',
        }

        response = requests.post(face_api_url, params=params, headers=headers, json={"url": image_url})

        raw = json.dumps(response.json())  # json으로 데이터 받아옴
        raw2 = raw.strip('[]')  # 대괄호 제거

        result = json.loads(raw2)  # 데이터 딕셔너리 형식으로 변환 (수치 가져오기 위해서)

        ## DB로 보낼 데이터
        pupilleftx = result["faceLandmarks"]["pupilLeft"]['x']  # 왼쪽 x


        pupillefty = result["faceLandmarks"]["pupilLeft"]['y']  # 왼쪽 y

        pupilrightx = result["faceLandmarks"]["pupilRight"]['x']  # 오른쪽 x

        pupilrighty = result["faceLandmarks"]["pupilRight"]['y']  # 오른쪽 y


        ## gif 박스 그릴 데이터

        EyeLeftOuterX = result["faceLandmarks"]["eyeLeftOuter"]['x']  # 왼쪽 x

        EyeRightOuterX = result["faceLandmarks"]["eyeRightOuter"]['x']  # 오른쪽 x

        EyeLeftTopY = result["faceLandmarks"]["eyeLeftTop"]['y']  # 왼쪽 y

        EyeRightTopY = result["faceLandmarks"]["eyeRightTop"]['y']  # 왼쪽 y

        EyeLeftBottomY = result["faceLandmarks"]["eyeLeftBottom"]['y']  # 오른쪽 y

        EyeRightBottomY = result["faceLandmarks"]["eyeRightBottom"]['y']  # 오른쪽 y


        if(EyeLeftTopY < EyeRightTopY):
            EyeTopY = EyeLeftTopY
        else:
            EyeTopY = EyeRightTopY

        if(EyeLeftBottomY > EyeRightBottomY):
            EyeBottomY = EyeLeftBottomY
        else:
            EyeBottomY = EyeRightBottomY

        boxSizeX = EyeRightOuterX - EyeLeftOuterX + 70
        boxSizeY = EyeBottomY - EyeTopY + 70
        boxStartX = EyeLeftOuterX - 25
        boxStartY = EyeTopY - 25

        box = []
        box.append(boxSizeX)
        box.append(boxSizeY)
        box.append(boxStartX)
        box.append(boxStartY)


        ####
        glassSizeX = (EyeRightOuterX - EyeLeftOuterX +90)/2
        glassSizeY = (EyeBottomY - EyeTopY+90) /2
        glassStartX = (EyeLeftOuterX-25) /2
        glassStartY = (EyeTopY-25)/2

        glass = []
        glass.append(glassSizeX)
        glass.append(glassSizeY)
        glass.append(glassStartX)
        glass.append(glassStartY)

        glass.append(glassStartX+glassSizeX)
        glass.append(glassStartY+glassSizeY)

        glass_q.put(glass)

        pupilleftx =   pupilleftx +200
        pupillefty =  pupillefty-90

        pupilrightx =  pupilrightx +60
        pupilrighty =  pupilrighty-90

        count = 0
        tracker = EyeTribe()
        tracker.connect()
        tracker.pushmode()


        while count < 700:

            box_q.put(box)
            n = tracker.next()

            str_n = str(n)
            splt_n = str_n.split(';')


            splt_n[9] = float(splt_n[9])
            splt_n[10] = float(splt_n[10])
            splt_n[16] = float(splt_n[16])
            splt_n[17] = float(splt_n[17])

            ##안경맞추기

            x_goal.put(pupilrightx)
            y_goal.put(pupilrighty)

            x.put(pupilleftx)
            y.put(pupillefty)


            if count % 5 ==0:

                splt_n[5] = float(splt_n[5])  # 결합 x
                splt_n[6] = float(splt_n[6])  # 결합 y

                WebX=splt_n[5]
                WebY=splt_n[6]

                if WebX > 1728:
                    WebX = 9
                elif WebX > 1536:
                    WebX = 8
                elif WebX > 1344:
                    WebX = 7
                elif WebX > 1152:
                    WebX = 6
                elif WebX > 960:
                    WebX = 5
                elif WebX > 768:
                    WebX = 4
                elif WebX > 576:
                    WebX = 3
                elif WebX > 384:
                    WebX = 2
                elif WebX > 192:
                    WebX = 1
                else:
                    WebX = 0

                if WebY > 972:
                    WebY = 9
                elif WebY > 864:
                    WebY = 8
                elif WebY > 756:
                    WebY = 7
                elif WebY > 648:
                    WebY = 6
                elif WebY > 540:
                    WebY = 5
                elif WebY > 432:
                    WebY = 4
                elif WebY > 324:
                    WebY = 3
                elif WebY > 216:
                    WebY = 2
                elif WebY > 108:
                    WebY = 1
                else:
                    WebY = 0

                points.append((WebX, WebY))
                for p in points:
                    child_eye_data[p[0]][p[1]] += 1

            count += 1

        tracker.pullmode()
        tracker.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Eye()

    sys.exit(app.exec_())