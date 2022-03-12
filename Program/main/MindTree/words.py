from PyQt5.QtWidgets import QMainWindow, QApplication, QAbstractButton, QGraphicsDropShadowEffect, QLabel
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5 import QtCore
import sys

class PicButton(QAbstractButton):
    def __init__(self, pixmap, parent=None):
        super(PicButton, self).__init__(parent)
        self.pixmap = pixmap

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

    def sizeHint(self):
        return self.pixmap.size()

class WordWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color: black;")
        self.setGeometry(460, 240, 1000, 600)
        self.setFixedSize(1000, 600)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        self.btn = PicButton(QPixmap('뒤로가기_pink.png'), self) #나가기
        self.btn.resize(60, 60)
        self.btn.move(25, 20)
        effect = QGraphicsDropShadowEffect(blurRadius=5, xOffset=3, yOffset=3)
        self.btn.setGraphicsEffect(effect)
        self.btn.clicked.connect(self.close)

        self.frame = QLabel(self)
        # self.frame.setStyleSheet("border-image:url(wordcloud_without_axisoff2.png);")
        self.frame.setStyleSheet("border-image:url(C:/MindTree2/Wordcloud/wordcloud_without_axisoff2.png);")
        self.frame.resize(800, 550)
        self.frame.move(100, 33)
        self.frame.show()

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = WordWindow()
    sys.exit(app.exec_())
