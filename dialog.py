#!/usr/bin/env python
# --*--encoding:utf8--*--

import os
import pwd
from PyQt5 import QtCore
from PyQt5.QtWidgets import *


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.setFixedSize(400, 250)
        self.nameLabel = QLabel('Name:')
        self.passwdLabel = QLabel('Password:')
        self.nameEdit = QLineEdit()
        self.passwdEdit = QLineEdit()
        self.nameEdit.setText(pwd.getpwuid(os.getuid()).pw_name)
        self.passwdEdit.setEchoMode(QLineEdit.Password)

        self.buttonBox = QDialogButtonBox()
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)

        self.registerRadio = QRadioButton('Register')
        self.visitorRadio = QRadioButton('Visitor')
        self.registerRadio.setChecked(True)

        self.groupBox = QGroupBox('Login')
        self.groupBox.setStyleSheet('''
        QGroupBox
        {
            font-size: 18px;
            font-weight: bold;
            font-family: Monaco
        }
        ''')
        self.layout = QGridLayout()
        self.layout.addWidget(self.registerRadio, 0, 0, 2, 1)
        self.layout.addWidget(self.visitorRadio, 1, 0, 3, 1)
        self.layout.addWidget(self.nameLabel, 3, 0, 3, 1)
        self.layout.addWidget(self.nameEdit, 3, 1, 3, 1)
        self.layout.addWidget(self.passwdLabel, 4, 0, 6, 1)
        self.layout.addWidget(self.passwdEdit, 4, 1, 6, 1)
        self.groupBox.setLayout(self.layout)
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.groupBox)
        self.mainLayout.addWidget(self.buttonBox)
        self.setLayout(self.mainLayout)

        self.registerRadio.clicked.connect(self.enableEdit)
        self.visitorRadio.clicked.connect(self.disableEdit)

        self.nameEdit.textEdited.connect(self.checkNameEdit)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.show()
        self.isAccepted = self.exec_()

    def checkNameEdit(self):
        if not self.nameEdit.text() and not self.visitorRadio.isChecked():
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        elif self.nameEdit.text() and self.registerRadio.isChecked():
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)

    def enableEdit(self):
        self.nameEdit.setEnabled(True)
        self.passwdEdit.setEnabled(True)
        # self.checkNameEdit()
        # self.checkNameField()

    def disableEdit(self):
        self.nameEdit.setEnabled(False)
        self.passwdEdit.setEnabled(False)
        self.buttonBox.button(QDialogButtonBox.Ok).setFocus()


class BaseProgressWidget(QWidget):
    updateProgress = QtCore.pyqtSignal(str)

    def __init__(self, text='', parent=None):
        super(BaseProgressWidget, self).__init__(parent)
        self.setFixedHeight(50)
        self.text = text
        self.progressbar = QProgressBar()
        self.progressbar.setTextVisible(True)
        self.updateProgress.connect(self.set_value)

        self.bottomBorder = QWidget()
        self.bottomBorder.setStyleSheet("""
            background: palette(shadow);
        """)
        self.bottomBorder.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed))
        self.bottomBorder.setMinimumHeight(1)

        self.label = QLabel(self.text)
        self.label.setStyleSheet("""
            font-weight: bold;
        """)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10, 0, 10, 0)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.progressbar)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.addLayout(self.layout)
        self.mainLayout.addWidget(self.bottomBorder)
        self.setLayout(self.mainLayout)
        self.totalValue = 0

    def set_value(self, value):
        self.totalValue += len(value)
        self.progressbar.setValue(self.totalValue)

    def set_max(self, value):
        self.progressbar.setMaximum(value)


class DownloadProgressWidget(BaseProgressWidget):
    def __init__(self, text='Downloading', parent=None):
        super(self.__class__, self).__init__(text, parent)
        style = """
        QProgressBar {
            border: 2px solid grey;
            border-radius: 5px;
            text-align: center;
        }

        QProgressBar::chunk {
            background-color: #37DA7E;
            width: 20px;
        }"""
        self.progressbar.setStyleSheet(style)


class UploadProgressWidget(BaseProgressWidget):
    def __init__(self, text='Uploading', parent=None):
        super(self.__class__, self).__init__(text, parent)
        style = """
        QProgressBar {
            border: 2px solid grey;
            border-radius: 5px;
            text-align: center;
        }

        QProgressBar::chunk {
            background-color: #88B0EB;
            width: 20px;
        }"""
        self.progressbar.setStyleSheet(style)


class ProgressDialog(QMainWindow):
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.resize(500, 250)
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.setCentralWidget(self.scrollArea)

        self.centralWidget = QWidget()
        self.scrollArea.setWidget(self.centralWidget)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(QtCore.Qt.AlignTop)
        self.layout.setContentsMargins(0, 10, 0, 0)
        self.centralWidget.setLayout(self.layout)

    def addProgressbar(self, progressbar):
        self.layout.addWidget(progressbar)

    def addProgress(self, type, title, size):
        if type not in ['download', 'upload']:
            raise str("type must 'download' or 'upload'")

        if type == 'download':
            pb = DownloadProgressWidget(text=title)
        else:
            pb = UploadProgressWidget(text=title)
        pb.set_max(size)
        self.addProgressbar(pb)
        return pb


def loginDialog(parent=None):
    login = LoginDialog(parent)
    if not login.isAccepted:
        return False
    elif login.visitorRadio.isChecked():
        return 'anonymous', 'anonymous', True
    else:
        return str(login.nameEdit.text()), str(login.passwdEdit.text()), True


if __name__ == '__main__':
    def testLoinDialog():
        app = QApplication([])
        print(loginDialog())


    def testProgressDialog():
        p = ProgressDialog()


    def testProgressDialog():
        import random
        number = [x for x in range(1, 101)]
        progresses = []
        while len(progresses) <= 20: progresses.append(random.choice(number))
        app = QApplication([])
        pbs = ProgressDialog()
        for i in progresses:
            pb = pbs.addProgress(type='download', title='download', size=100)
            pb.set_value(' ' * i)

        for i in progresses:
            pb = pbs.addProgress(type='upload', title='upload', size=100)
            pb.set_value(' ' * i)
        pbs.show()
        app.exec_()


    testProgressDialog()
    testLoinDialog()
