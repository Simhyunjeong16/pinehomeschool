import sys
from queue import Queue
import pymysql
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class PicButton(QAbstractButton):
    def __init__(self, pixmap, parent=None):
        super(PicButton, self).__init__(parent)
        self.pixmap = pixmap

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

    def sizeHint(self):
        return self.pixmap.size()

class GIFLabel(QLabel):
    def __init__(self, gif, *args, **kwargs):
        QLabel.__init__(self, *args, **kwargs)

        movie = QMovie(gif)
        self.setMovie(movie)
        movie.start()


CoinQ = Queue(100)
class CountStar(QObject):

    signalExample = QtCore.pyqtSignal()
    signalExample2 = QtCore.pyqtSignal()
    signalExample3 = QtCore.pyqtSignal()
    signalExample4 = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

    @QtCore.pyqtSlot()
    def star_get(self):
        connection_c = pymysql.connect(host='203.252.208.222', user='root', password='MindTree@12345', db='box_schema',
                                       port=8008)
        try:
            with connection_c.cursor() as cursor:
                sql = "select value from pickup_box ORDER BY time DESC limit 1"
                cursor.execute(sql)
                coins = cursor.fetchone()
        finally:
            connection_c.close()

        product = CoinQ.get()

        if product == 1:#400코인

            if coins[0] - 400 < 0:
                self.signalExample.emit()

            else:
                connection6 = pymysql.connect(host='203.252.208.222', user='root', password='MindTree@12345',
                                          db='box_schema', port=8008)
                with connection6.cursor() as cursor:
                    sql = 'INSERT INTO pickup_box (value) VALUES ( %s )'
                    cursor.execute(sql, (coins[0] - 400))
                    connection6.commit()
                    connection6.close()

                self.signalExample2.emit()


        elif product == 2:#800코인

            if coins[0] - 800 < 0:
                self.signalExample.emit()

            else :
                connection6 = pymysql.connect(host='203.252.208.222', user='root', password='MindTree@12345',
                                              db='box_schema', port=8008)
                with connection6.cursor() as cursor:
                    sql = 'INSERT INTO pickup_box (value) VALUES ( %s )'
                    cursor.execute(sql, (coins[0] - 800))
                    connection6.commit()
                    connection6.close()

                self.signalExample3.emit()

        elif product == 3:#1600코인

            if coins[0] - 1600 < 0:
                self.signalExample.emit()

            else:
                connection6 = pymysql.connect(host='203.252.208.222', user='root', password='MindTree@12345',
                                              db='box_schema', port=8008)
                with connection6.cursor() as cursor:
                    sql = 'INSERT INTO pickup_box (value) VALUES ( %s )'
                    cursor.execute(sql, (coins[0] - 1600))
                    connection6.commit()
                    connection6.close()

                self.signalExample4.emit()
            


class BoxWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color: rgb(60, 186, 255);")
        self.setGeometry(460, 240, 1000, 600)
        self.setFixedSize(1000, 600)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        self.frame = QLabel(self)
        self.frame.setStyleSheet("border-image:url(money.png);")
        self.frame.resize(80, 80)
        self.frame.move(655, 33) # 코인 사진
        self.frame.show()

        self.btn = PicButton(QPixmap('뒤로가기_pink.png'), self) #나가기
        self.btn.resize(60, 60)
        self.btn.move(25, 20)
        effect = QGraphicsDropShadowEffect(blurRadius=5, xOffset=3, yOffset=3)
        self.btn.setGraphicsEffect(effect)
        self.btn.clicked.connect(self.forceWorkerReset)

        self.g1 = PicButton(QPixmap('chocolate.png'), self)
        self.g1.resize(200, 200)
        self.g1.move(100, 200)
        self.g1.show()
        self.g1.clicked.connect(self.minus1)

        self.gc1 = QLabel(self)
        self.gc1.setText("400코인")
        self.gc1.move(150, 420)
        self.gc1.resize(150, 100)
        self.gc1.setStyleSheet('font-size: 40pt; font-family: 스웨거 TTF;')
        self.gc1.show()

        self.g2 = PicButton(QPixmap('robot.png'), self)
        self.g2.resize(200, 200)
        self.g2.move(400, 200)
        self.g2.show()
        self.g2.clicked.connect(self.minus2)

        self.gc2 = QLabel(self)
        self.gc2.setText("800코인")
        self.gc2.move(440, 420)
        self.gc2.resize(150, 100)
        self.gc2.setStyleSheet('font-size: 40pt; font-family: 스웨거 TTF;')
        self.gc2.show()

        self.g3 = PicButton(QPixmap('joystick.png'), self)
        self.g3.resize(200, 200)
        self.g3.move(700, 200)
        self.g3.show()
        self.g3.clicked.connect(self.minus3)

        self.gc3 = QLabel(self)
        self.gc3.setText("1600코인")
        self.gc3.move(730, 420)
        self.gc3.resize(150, 100)
        self.gc3.setStyleSheet('font-size: 40pt; font-family: 스웨거 TTF;')
        self.gc3.show()

        self.ChangeCoin()

        self.worker4 = CountStar()  # 백그라운드에서 돌아갈 인스턴스 소환
        self.worker_thread4 = QThread()  # 따로 돌아갈 thread를 하나 생성
        self.worker4.moveToThread(self.worker_thread4)  # worker를 만들어둔 쓰레드에 넣어줍니다
        self.worker4.signalExample.connect(self.signalMethodExample)
        self.worker4.signalExample2.connect(self.signalMethodExample2)
        self.worker4.signalExample3.connect(self.signalMethodExample3)
        self.worker4.signalExample4.connect(self.signalMethodExample4)
        self.worker_thread4.start()  # 쓰레드를 실행합니다.
        self.tt4 = QTimer()
        self.tt4.start()
        self.tt4.timeout.connect(self.worker4.star_get)

        self.show()


    def ChangeCoin(self):
        connection_p = pymysql.connect(host='203.252.208.222', user='root', password='MindTree@12345', db='box_schema',
                                       port=8008)
        try:
            with connection_p.cursor() as cursor:
                sql = "select value from pickup_box ORDER BY time DESC limit 1"
                cursor.execute(sql)
                coins__ = cursor.fetchone()
        finally:
            connection_p.close()

        self.score = QLabel(self)
        self.score.setText("X " + str(coins__[0]))
        self.score.move(750, 30)
        self.score.resize(200, 100)
        self.score.setStyleSheet('font-size: 60pt; font-family: 스웨거 TTF; color: white;')
        self.score.show()

    def signalMethodExample2(self):
        a = QPixmap("획득_초코렛.png")
        a = a.scaled(300, 300)

        msg = QMessageBox()
        msg.setWindowTitle("상품 구입")
        msg.setStyleSheet("background-color: rgb(255, 191, 204);")
        msg.setWindowIcon(QIcon("mainlogo.png"))

        msg.setIcon(QMessageBox.Information)
        msg.setIconPixmap(a)  # 옆에 뜨는 이미지!!!

        msg.setStandardButtons(QMessageBox.Ok)
        buttonOK = msg.button(QMessageBox.Ok)
        buttonOK.setStyleSheet("background-color: rgb(255, 255, 255);")
        buttonOK.setText('사러가기')
        msg.buttonClicked.connect(self.ChangeCoin)

        msg.exec_()

    def signalMethodExample3(self):
        a = QPixmap("획득_장난감.png")
        a = a.scaled(300, 300)

        msg = QMessageBox()
        msg.setWindowTitle("상품 구입")
        msg.setStyleSheet("background-color: rgb(255, 191, 204);")
        msg.setWindowIcon(QIcon("mainlogo.png"))

        msg.setIcon(QMessageBox.Information)
        msg.setIconPixmap(a)  # 옆에 뜨는 이미지!!!

        msg.setStandardButtons(QMessageBox.Ok)
        buttonOK = msg.button(QMessageBox.Ok)
        buttonOK.setStyleSheet("background-color: rgb(255, 255, 255);")
        buttonOK.setText('사러가기')
        msg.buttonClicked.connect(self.ChangeCoin)

        msg.exec_()

    def signalMethodExample4(self):
        a = QPixmap("획득_게임기.png")
        a = a.scaled(300, 300)

        msg = QMessageBox()
        msg.setWindowTitle("상품 구입")
        msg.setStyleSheet("background-color: rgb(255, 191, 204);")
        msg.setWindowIcon(QIcon("mainlogo.png"))

        msg.setIcon(QMessageBox.Information)
        msg.setIconPixmap(a)  # 옆에 뜨는 이미지!!!

        msg.setStandardButtons(QMessageBox.Ok)
        buttonOK = msg.button(QMessageBox.Ok)
        buttonOK.setStyleSheet("background-color: rgb(255, 255, 255);")
        buttonOK.setText('사러가기')
        msg.buttonClicked.connect(self.ChangeCoin)

        msg.exec_()

    def signalMethodExample(self):
        a = QPixmap("코인부족.png")
        a = a.scaled(300, 300)

        msg = QMessageBox()
        msg.setWindowTitle("코인 부족")
        msg.setStyleSheet("background-color: rgb(255, 191, 204);")
        msg.setWindowIcon(QIcon("mainlogo.png"))

        msg.setIcon(QMessageBox.Information)
        msg.setIconPixmap(a)  # 옆에 뜨는 이미지!!!

        msg.setStandardButtons(QMessageBox.Ok)
        buttonOK = msg.button(QMessageBox.Ok)
        buttonOK.setStyleSheet("background-color: rgb(255, 255, 255);")
        buttonOK.setText('나가기')

        msg.exec_()


    def minus1(self):
        CoinQ.put(1)

    def minus2(self):
        CoinQ.put(2)

    def minus3(self):
        CoinQ.put(3)


    def forceWorkerReset(self):
        if self.worker_thread4.isRunning():  # 쓰레드가 돌아가고 있다면
            self.worker_thread4.terminate()  # 현재 돌아가는 thread 를 중지시킨다

        self.close() #창 닫기



if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = BoxWindow()
    sys.exit(app.exec_())