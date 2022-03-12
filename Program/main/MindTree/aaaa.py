import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore, QtGui, QtWidgets
import cv2
from ui_main_window import *
import time
import requests
import json
import pymysql




class InfoWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setGeometry(170, 100, 1600, 900)
        self.setFixedSize(1600, 900)
        self.setWindowTitle("도움말")
        self.setWindowIcon(QIcon('info_.png'))

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.lbl1 = QLabel(self)
        self.lbl1.setStyleSheet("border-image:url(도움말.png);")
        self.lbl1.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.lbl1)



if __name__ == '__main__':
    app = QApplication(sys.argv)

    infowindow = InfoWindow()
    infowindow.show()

    sys.exit(app.exec_())