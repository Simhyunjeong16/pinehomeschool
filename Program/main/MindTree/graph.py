import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import pymysql
import webbrowser
import words
from words import *
import heatmap
from heatmap import *

class PicButton(QAbstractButton):
    def __init__(self, pixmap, parent=None):
        super(PicButton, self).__init__(parent)
        self.pixmap = pixmap

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

    def sizeHint(self):
        return self.pixmap.size()


class GGG(QMainWindow):
    def __init__(self):
        super().__init__()

        # 오늘 학습한 수치 모두 가져오는 코드
        e_connection = pymysql.connect(host='203.252.208.222', user='root', password='MindTree@12345', db='emotion_sum',
                                       port=8008)

        try:
            with e_connection.cursor() as cursor:  # emotion_sum
                sql = "select plus, emot from emotion_sum where timestamp >= curdate()"
                cursor.execute(sql)
                emo_sum = cursor.fetchall()

        finally:
            e_connection.close()

        self.setGeometry(0, 0, 1920, 1080)
        self.setFixedSize(1920, 1080)

        self.setWindowTitle("파인 홈스쿨")
        self.setWindowIcon(QIcon('mainlogo.png'))

        self.setStyleSheet("border-image:url(오늘의학습.png);")
        self.UI()

        happy_sum = 0.0
        sad_sum = 0.0
        angry_sum = 0.0
        surprise_sum = 0.0

        happy_count = 0
        sad_count = 0
        angry_count = 0
        surprise_count = 0


        for i in range(emo_sum.__len__()):
            # print(emo_sum[i][0], emo_sum[i][1])  # emo_sum[i][0] -> 감정 수치 && emo_sum[i][1] -> 감정 번호 (1: 행복, 2:슬픔. 3:화남, 4:놀라움, 5:시선)

            if (emo_sum[i][1] == 1):
                happy_sum += emo_sum[i][0]
                happy_count += 1

            elif (emo_sum[i][1] == 2):
                sad_sum += emo_sum[i][0]
                sad_count += 1

            elif (emo_sum[i][1] == 3):
                angry_sum += emo_sum[i][0]
                angry_count += 1

            elif (emo_sum[i][1] == 4):
                surprise_sum += emo_sum[i][0]
                surprise_count += 1


        try:
            happy_aver = happy_sum / happy_count

        except ZeroDivisionError:  # no data 사진 출력! 학습을 안 한 상태
            happy_aver = -1

        try:
            sad_aver = sad_sum / sad_count

        except ZeroDivisionError:  # no data 사진 출력! 학습을 안 한 상태
            sad_aver = -1

        try:
            angry_aver = angry_sum / angry_count

        except ZeroDivisionError:  # no data 사진 출력! 학습을 안 한 상태
            angry_aver = -1

        try:
            surprise_aver = surprise_sum / surprise_count

        except ZeroDivisionError:  # no data 사진 출력! 학습을 안 한 상태
            surprise_aver = -1


        # print("happy_aver:" + str(happy_aver))
        # print("sad_aver:" + str(sad_aver))
        # print("angry_aver:" + str(angry_aver))
        # print("surprise_aver:" + str(surprise_aver))
        # print("look_aver:" + str(look_aver))


        if happy_aver == -1:
            self.frame3 = QLabel(self)
            self.frame3.setStyleSheet("border-image:url(학습그래프NO.png);")
            self.frame3.resize(210, 220)
            self.frame3.move(250, 390)   # (300, 350)
            self.frame3.show()

        elif happy_aver > 70:
            self.frame = QLabel(self)
            self.frame.setStyleSheet("border-image:url(학습그래프A.png);")
            self.frame.resize(230, 240)
            self.frame.move(250, 380)
            self.frame.show()

        elif happy_aver > 50:
            self.frame1 = QLabel(self)
            self.frame1.setStyleSheet("border-image:url(학습그래프B.png);")
            self.frame1.resize(230, 240)
            self.frame1.move(240, 380)
            self.frame1.show()

        else:
            self.frame2 = QLabel(self)
            self.frame2.setStyleSheet("border-image:url(학습그래프C.png);")
            self.frame2.resize(230, 240)
            self.frame2.move(240, 380)
            self.frame2.show()


        if sad_aver == -1:
            self.frame3 = QLabel(self)
            self.frame3.setStyleSheet("border-image:url(학습그래프NO.png);")
            self.frame3.resize(210, 220)
            self.frame3.move(550, 390)  # (600, 350)
            self.frame3.show()

        elif sad_aver > 70:
            self.frame = QLabel(self)
            self.frame.setStyleSheet("border-image:url(학습그래프A.png);")
            self.frame.resize(230, 240)
            self.frame.move(550, 380)
            self.frame.show()

        elif sad_aver > 50:
            self.frame1 = QLabel(self)
            self.frame1.setStyleSheet("border-image:url(학습그래프B.png);")
            self.frame1.resize(230, 240)
            self.frame1.move(540, 380)
            self.frame1.show()

        else:
            self.frame2 = QLabel(self)
            self.frame2.setStyleSheet("border-image:url(학습그래프C.png);")
            self.frame2.resize(230, 240)
            self.frame2.move(540, 380)
            self.frame2.show()

        if angry_aver == -1:
            self.frame3 = QLabel(self)
            self.frame3.setStyleSheet("border-image:url(학습그래프NO.png);")
            self.frame3.resize(210, 220)
            self.frame3.move(850, 390)  # (900, 350)
            self.frame3.show()

        elif angry_aver > 70:
            self.frame = QLabel(self)
            self.frame.setStyleSheet("border-image:url(학습그래프A.png);")
            self.frame.resize(230, 240)
            self.frame.move(850, 380)
            self.frame.show()

        elif angry_aver > 50:
            self.frame1 = QLabel(self)
            self.frame1.setStyleSheet("border-image:url(학습그래프B.png);")
            self.frame1.resize(230, 240)
            self.frame1.move(840, 380)
            self.frame1.show()

        else:
            self.frame2 = QLabel(self)
            self.frame2.setStyleSheet("border-image:url(학습그래프C.png);")
            self.frame2.resize(230, 240)
            self.frame2.move(840, 380)
            self.frame2.show()

        if surprise_aver == -1:
            self.frame3 = QLabel(self)
            self.frame3.setStyleSheet("border-image:url(학습그래프NO.png);")
            self.frame3.resize(210, 220)
            self.frame3.move(1150, 390)  # (1200, 350)
            self.frame3.show()

        elif surprise_aver > 70:
            self.frame = QLabel(self)
            self.frame.setStyleSheet("border-image:url(학습그래프A.png);")
            self.frame.resize(230, 240)
            self.frame.move(1150, 380)
            self.frame.show()

        elif surprise_aver > 50:
            self.frame1 = QLabel(self)
            self.frame1.setStyleSheet("border-image:url(학습그래프B.png);")
            self.frame1.resize(230, 240)
            self.frame1.move(1140, 380)
            self.frame1.show()

        else:
            self.frame2 = QLabel(self)
            self.frame2.setStyleSheet("border-image:url(학습그래프C.png);")
            self.frame2.resize(230, 240)
            self.frame2.move(1140, 380)
            self.frame2.show()

        self.show()



    def UI(self):
        self.frame = QLabel(self)
        self.frame.setStyleSheet("border-image:url(학습그래프버튼_행복.png);")
        self.frame.resize(250, 400)
        self.frame.move(230, 350)
        eff = QGraphicsDropShadowEffect()
        self.frame.setGraphicsEffect(eff)
        self.frame.show()

        self.frame1 = QLabel(self)
        self.frame1.setStyleSheet("border-image:url(학습그래프버튼_슬픔.png);")
        self.frame1.resize(250, 400)
        self.frame1.move(530, 350)
        eff1 = QGraphicsDropShadowEffect()
        self.frame1.setGraphicsEffect(eff1)
        self.frame1.show()

        self.frame2 = QLabel(self)
        self.frame2.setStyleSheet("border-image:url(학습그래프버튼_화남.png);")
        self.frame2.resize(250, 400)
        self.frame2.move(830, 350)
        eff2 = QGraphicsDropShadowEffect()
        self.frame2.setGraphicsEffect(eff2)
        self.frame2.show()

        self.frame3 = QLabel(self)
        self.frame3.setStyleSheet("border-image:url(학습그래프버튼_놀라움.png);")
        self.frame3.resize(250, 400)
        self.frame3.move(1130, 350)
        eff3 = QGraphicsDropShadowEffect()
        self.frame3.setGraphicsEffect(eff3)
        self.frame3.show()

        self.btn1 = PicButton(QPixmap('학습그래프버튼_아이시선알아보기.png'), self) #히트맵 버튼
        self.btn1.resize(250, 400)
        self.btn1.move(1430, 350)
        eff4 = QGraphicsDropShadowEffect()
        self.btn1.setGraphicsEffect(eff4)
        self.btn1.clicked.connect(self.hhh)

        self.btn5 = PicButton(QPixmap('뒤로가기_pink.png'), self)
        self.btn5.resize(100, 100)
        self.btn5.move(20, 950)
        self.btn5.clicked.connect(self.close)

        self.btn = PicButton(QPixmap('학습그래프버튼_kids.png'), self)
        self.btn.resize(450, 150)
        self.btn.move(430, 830)
        eff_ = QGraphicsDropShadowEffect()
        self.btn.setGraphicsEffect(eff_)
        self.btn.clicked.connect(self.word)

        self.btn = PicButton(QPixmap('학습그래프버튼_더자세히알아보기.png'), self)
        self.btn.resize(450, 150)
        self.btn.move(1043, 830)
        eff_ = QGraphicsDropShadowEffect()
        self.btn.setGraphicsEffect(eff_)
        self.btn.clicked.connect(self.show_grafana)


    def word(self):
        self.wc = words.WordWindow()
        self.wc.show()

    def hhh(self):
        self.hw = heatmap.HeatWindow()
        self.hw.show()

    def show_grafana(self):
        webbrowser.open("http://localhost:8080/d/0aFm4hKWz/gamjeonghagseub?orgId=1&from=1564585200000&to=1573743540000&kiosk")



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GGG()
    sys.exit(app.exec_())