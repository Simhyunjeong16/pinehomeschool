from PyQt5 import QtWidgets


class Ui_Form(object):

    def setupUi(self, Form):
        Form.setGeometry(0, 0, 1920, 1080)

        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.image_label = QtWidgets.QLabel(Form)

        self.image_label.move(500, 500)
        self.verticalLayout.addWidget(self.image_label)
