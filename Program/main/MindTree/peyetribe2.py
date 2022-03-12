import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from main_window import *
import main_window
from ui_main_window import *
import cv2
import urllib.request
import pymysql
# from peyetribe import EyeTribe
from threading import Thread
import threading
import time
import numpy as np
import cv2
import math
from PyQt5.QtGui import QPainter, QBrush, QPen
from peyetribe import EyeTribe
from PyQt5.QtCore import Qt

from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QBrush, QImage, QPainter, QPixmap, QWindow
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget

# 제일 최근 이미지를 가져오기 위한 코드 #
connection = pymysql.connect(host='203.252.208.222', user='root', password='MindTree@12345', db='imageupload', port=8008)

try:
    with connection.cursor() as cursor:  # 최신사진
        sql = "select url from images ORDER BY id DESC limit 1"
        cursor.execute(sql)
        image_result = cursor.fetchone()

finally:
    connection.close()

box_q = Queue(BUF_SIZE)
signal_q = Queue(BUF_SIZE)
signal_c = Queue(BUF_SIZE)

xR = Queue(100)
yR = Queue(100)
xL = Queue(100)
yL = Queue(100)

class Eye(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setGeometry(0, 0, 1920, 1080)
        # self.setFixedSize(1920, 1000)

        self.setWindowTitle("파인 홈스쿨")
        self.setWindowIcon(QIcon('mainlogo.png'))

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        self.lay = QHBoxLayout(self.main_widget)

        self.lay.setContentsMargins(0, 0, 0, 0)
        # self.lay.setAlignment(Qt.AlignCenter)

        # 배경
        self.lbl1 = QLabel(self)
        self.lbl1.setStyleSheet("border-image:url(pineapple2_eye.png);")
        self.lbl1.setAlignment(Qt.AlignCenter)
        self.lay.addWidget(self.lbl1)
        # self.setStyleSheet("border-image:url(pineapple2_eye.png);") ##############배경임다.

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
        # self.parent.setAlignment(Qt.AlignCenter)  # 가운데 정렬 #안먹음

        # self.lay.addWidget(self.parent)  # lay에다가 추가하기
        # self.parent.show()

        self.show()

        tracker= Tracker()
        _eye = threading.Thread(target=tracker.eye_thread, daemon=True)
        _eye.start()
        print("_eye 쓰레드 시작")

        s = signal_q.get()
        c = signal_c.get()
        if s == 3:
            _box = threading.Thread(target=self.Drawbox(), daemon=True)
            _box.start()
            print("_box 쓰레드 시작")

        move_eye = threading.Thread(target=self.init_ui(), daemon=True)
        move_eye.start()
        print("move_eye 쓰레드 시작")

    def init_ui(self):
        _eye = threading.Thread(target=self.onMove, daemon=True)
        _eye.start()

        self.img = QLabel(self)  # 왼
        self.img2 = QLabel(self)  # 오

        pixmap = QPixmap("eye_show.png")  # 왼
        pixmap = pixmap.scaled(100, 40)  # 사이즈가 조정
        self.img.setPixmap(pixmap)
        self.img.setAlignment(Qt.AlignCenter)
        self.img.show()

        pixmap2 = QPixmap("eye_show.png")  # 오
        pixmap2 = pixmap2.scaled(100, 40)  # 사이즈가 조정
        self.img2.setPixmap(pixmap2)
        self.img2.setAlignment(Qt.AlignCenter)
        self.img2.show()

    def onMove(self):
        count =0
        i = 0
        tracker = EyeTribe()
        tracker.connect()
        tracker.pushmode()

        while True :
            n = tracker.next()
            str_n = str(n)
            splt_n = str_n.split(';')

            splt_n[9] = float(splt_n[9]) #왼x
            splt_n[10] = float(splt_n[10]) #왼y
            splt_n[16] = float(splt_n[16]) #오x
            splt_n[17] = float(splt_n[17]) #오y

            print("coord",splt_n[9], splt_n[10], splt_n[16], splt_n[17])

            if count % 10 == 0:
                xL.put(splt_n[9])
                yL.put(splt_n[10])

                xR.put(splt_n[16])
                yR.put(splt_n[17])

            if not xR.empty() and not yR.empty()and not xL.empty()and not yL.empty() :

                print("hey")
                Lx = xL.get()
                Ly = yL.get()

                Rx = xR.get()
                Ry = yR.get()

                if Rx == 0.0 and Ry == 0.0 :
                    self.img2.close() #close안먹음
                    self.img2.show()
                elif Lx == 0.0 and Ly == 0.0:

                    self.img.close()
                    self.img.show()
                else :
                    self.img.show()
                    self.img.move(Lx, Ly)
                    self.img2.move(Rx, Ry)
                    self.update()
                    print("0아님 Lx, Ly, Rx, Ry", Lx, Ly, Rx, Ry)

            print("count:", count)
            count += 1

        tracker.pullmode()
        tracker.close()

    def Drawbox(self):
        print("start!!!!")
        box_num = box_q.get()
        sizeX = int(box_num[0])
        sizeY = int(box_num[1])
        moveX = int(box_num[2])
        moveY = int(box_num[3])
        print(sizeX)
        print(box_num[1])

        self.label = GIFLabel("giphy.gif", self)
        self.label.move(moveX+275, moveY+20)
        self.label.setScaledContents(10)
        self.label.resize(sizeX, sizeY)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.show()

        self.t3 = QTimer()
        self.t3.start(10000)
        self.t3.timeout.connect(self.close_gif)

    def close_gif(self):
        print("AS")
        self.label.close()

class GIFLabel(QLabel):
    def __init__(self, gif, *args, **kwargs):
        QLabel.__init__(self, *args, **kwargs)

        movie = QMovie(gif)
        # self.move(750, 200)
        # self.setScaledContents(10)
        # self.resize(500, 200)

        self.setMovie(movie)
        movie.start()


class Point2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Tracker(QWidget): #QFrame
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

        print(result)

        pupilleft = result["faceLandmarks"]["pupilLeft"]  # 원하는 특정 값 가져오기

        print("부모님의 사진 눈좌표 : ", pupilleft)
        print("PUPIL LEFT:", result["faceLandmarks"]["pupilLeft"], ",", "PUPIL RIGHT:",
              result["faceLandmarks"]["pupilRight"])

        ## DB로 보낼 데이터
        pupilleftx = result["faceLandmarks"]["pupilLeft"]['x']  # 왼쪽 x
        print("pupilleftx:", pupilleftx)

        pupillefty = result["faceLandmarks"]["pupilLeft"]['y']  # 왼쪽 y
        print("pupillefty:", pupillefty)

        pupilrightx = result["faceLandmarks"]["pupilRight"]['x']  # 오른쪽 x
        print("pupilrightx:", pupilrightx)

        pupilrighty = result["faceLandmarks"]["pupilRight"]['y']  # 오른쪽 y
        print("pupilrighty:", pupilrighty)


        ## gif 박스 그릴 데이터

        EyeLeftOuterX = result["faceLandmarks"]["eyeLeftOuter"]['x']  # 왼쪽 x
        print("EyeLeftOuterX:", EyeLeftOuterX)

        EyeLeftOuterY = result["faceLandmarks"]["eyeLeftOuter"]['y']  # 왼쪽 y
        print("EyeLeftOuterY:", EyeLeftOuterY)

        EyeRightOuterX = result["faceLandmarks"]["eyeRightOuter"]['x']  # 오른쪽 x
        print("EyeRightOuterX:", EyeRightOuterX)

        EyeRightOuterY = result["faceLandmarks"]["eyeRightOuter"]['y']  # 오른쪽 y
        print("EyeRightOuterY:", EyeRightOuterY)

        EyeLeftTopX = result["faceLandmarks"]["eyeLeftTop"]['x']  # 왼쪽 x
        print("EyeLeftTopX:", EyeLeftTopX)

        EyeLeftTopY = result["faceLandmarks"]["eyeLeftTop"]['y']  # 왼쪽 y
        print("EyeLeftTopY:", EyeLeftTopY)

        EyeRightTopX = result["faceLandmarks"]["eyeRightTop"]['x']  # 왼쪽 x
        print("EyeRightTopX:", EyeRightTopX)

        EyeRightTopY = result["faceLandmarks"]["eyeRightTop"]['y']  # 왼쪽 y
        print("EyeRightTopY:", EyeRightTopY)

        EyeLeftBottomX = result["faceLandmarks"]["eyeLeftBottom"]['x']  # 오른쪽 x
        print("EyeLeftBottomX:", EyeLeftBottomX)

        EyeLeftBottomY = result["faceLandmarks"]["eyeLeftBottom"]['y']  # 오른쪽 y
        print("EyeLeftBottomY:", EyeLeftBottomY)

        EyeRightBottomX = result["faceLandmarks"]["eyeRightBottom"]['x']  # 오른쪽 x
        print("EyeRightBottomX:", EyeRightBottomX)

        EyeRightBottomY = result["faceLandmarks"]["eyeRightBottom"]['y']  # 오른쪽 y
        print("EyeRightBottomY:", EyeRightBottomY)

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

        count = 0

        # 엄마 좌표는 옮긴 수치 + 좌표값
        # 아이 눈 좌표는 그대로
        pupilleftx = 560 + pupilleftx  # 500 값은 현정이가 정해주면 바꾸기!!!
        pupillefty = 90 + pupillefty

        pupilrightx = 560 + pupilrightx
        pupilrighty = 90 + pupilrighty

        count = 1

        tracker = EyeTribe()
        tracker.connect()
        tracker.pushmode()

        connection = pymysql.connect(host='203.252.208.222', user='root', password='MindTree@12345', db='pupil_schema', port=8008)

        while count < 200:
            print("count", count)
            n = tracker.next()
            print(n)
            str_n = str(n)
            splt_n = str_n.split(';')
            print(" splt_n", splt_n)
            # 비교
            pupilleftx_a = int(pupilleftx + 10)
            pupilleftx_s = int(pupilleftx - 10)
            pupillefty_a = int(pupillefty + 10)
            pupillefty_s = int(pupillefty - 10)
            # print(type(pupilleftx_a))

            pupilrightx_a = int(pupilrightx + 10)
            pupilrightx_s = int(pupilrightx - 10)
            pupilrighty_a = int(pupilrighty + 10)
            pupilrighty_s = int(pupilrighty - 10)

            splt_n[9] = float(splt_n[9])
            splt_n[10] = float(splt_n[10])
            splt_n[16] = float(splt_n[16])
            splt_n[17] = float(splt_n[17])
            ######
            p1 = Point2D(x=pupilleftx_s, y=pupilleftx_a)  # left점1
            p2 = Point2D(x=splt_n[9], y=splt_n[10])  # left점2

            p3 = Point2D(x=pupilrightx_s, y=pupilrightx_a)  # right점1
            p4 = Point2D(x=splt_n[16], y=splt_n[17])  # right점2

            a = p2.x - p1.x  # 선 a의 길이
            b = p2.y - p1.y  # 선 b의 길이

            c = p4.x - p3.x  # 선 c의 길이
            d = p4.y - p3.y  # 선 d의 길이

            e = math.sqrt(math.pow(a, 2) + math.pow(b, 2))  # 제곱근을 구함
            f = math.sqrt(math.pow(c, 2) + math.pow(d, 2))
            print("ef", e, f)

            if e <= 750 and f <= 1000:
                signal_c.put(4)
                print("123")
                print("참 잘했어요!")
                print("왼x", pupilleftx_s, splt_n[9], pupilleftx_a)
                print("왼y", pupillefty_s, splt_n[10], pupillefty_a)
                print("오x", pupilrightx_s, splt_n[16], pupilrightx_a)
                print("오y", pupilrighty_s, splt_n[17], pupilrighty_a)
                # 참 잘했어요!


            else:
                print("눈에서 불빛")

              #  count = 3
              #  if count == 3:
              #      print("QAWRQ")
                box_q.put(box)
                signal_q.put(3)


                print("1234")
                print("왼x", pupilleftx_s, splt_n[9], pupilleftx_a)
                print("왼y", pupillefty_s, splt_n[10], pupillefty_a)
                print("오x", pupilrightx_s, splt_n[16], pupilrightx_a)
                print("오y", pupilrighty_s, splt_n[17], pupilrighty_a)

            with connection.cursor() as cursor:
                sql = 'INSERT INTO pupil_value (id, img_lX, img_lY, img_rX, img_rY,webcam_lX,webcam_lY,webcam_rX,webcam_rY ) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s )'
                cursor.execute(sql, (
                    count, pupilleftx, pupillefty, pupilrightx, pupilrighty, splt_n[9], splt_n[10], splt_n[16],
                    splt_n[17]))
            connection.commit()
            print(cursor.lastrowid)
            count += 1

        connection.close()

        tracker.pullmode()

        tracker.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Eye()

    sys.exit(app.exec_())