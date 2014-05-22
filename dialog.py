#!/usr/bin/python
from PyQt4 import QtGui 
from PyQt4 import QtCore 

class LoginDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(LoginDialog, self).__init__(parent)
        import os, pwd
        self.setFixedSize(400, 250)
        self.nameLabel     = QtGui.QLabel('Name:')
        self.passwordLabel = QtGui.QLabel('Password:')
        self.nameEdit      = QtGui.QLineEdit( )
        self.passwordEdit  = QtGui.QLineEdit( )
        self.nameEdit.setText(pwd.getpwuid(os.getuid()).pw_name)
        self.passwordEdit.setEchoMode(QtGui.QLineEdit.Password)

        self.buttonBox = QtGui.QDialogButtonBox( )
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)

        self.registerRadio = QtGui.QRadioButton('Register')
        self.visitorRadio  = QtGui.QRadioButton('Visitor')
        self.registerRadio.setChecked(True)

        self.groupBox = QtGui.QGroupBox('Login')
        self.groupBox.setStyleSheet('''
        QGroupBox
        {
            font-size: 18px;
            font-weight: bold;
            font-family: Monaco
        }
        ''')
        self.layout = QtGui.QGridLayout( )
        self.layout.addWidget(self.registerRadio, 0, 0, 2, 1)
        self.layout.addWidget(self.visitorRadio,  1, 0, 3, 1)
        self.layout.addWidget(self.nameLabel,     3, 0, 3, 1)
        self.layout.addWidget(self.nameEdit,      3, 1, 3, 1)
        self.layout.addWidget(self.passwordLabel, 4, 0, 6, 1)
        self.layout.addWidget(self.passwordEdit,  4, 1, 6, 1)
        self.groupBox.setLayout(self.layout)
        self.mainLayout = QtGui.QVBoxLayout( )
        self.mainLayout.addWidget(self.groupBox)
        self.mainLayout.addWidget(self.buttonBox)
        self.setLayout(self.mainLayout)

        self.registerRadio.clicked.connect(self.enableEdit)
        self.visitorRadio.clicked.connect(self.disableEdit)

        self.nameEdit.textEdited.connect(self.checkNameField)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.show( )
        self.isAccepted = self.exec_( )

    def checkNameField(self):
        if not self.nameEdit.text( ) and not self.visitorRadio.isChecked( ):
            self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)
        elif self.nameEdit.text( ) and self.registerRadio.isChecked( ):
            self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
            
    def enableEdit(self):
        self.nameEdit.setEnabled(True)
        self.passwordEdit.setEnabled(True)
        self.checkNameField( )

    def disableEdit(self):
        self.nameEdit.setEnabled(False)
        self.passwordEdit.setEnabled(False)
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setFocus( )


class progressBar(QtGui.QProgressBar):
    updateProgressBar = QtCore.pyqtSignal(int)
    def __init__(self, total, parent=None):
        super(progressBar, self).__init__(parent)
        self.total = int(total)
        self.progress = [0, 0]
        self.setMaximum(self.total)

    def updateProgress(self, received):
        self.setValue(received)
        self.setFormat('%s/%s' % (received, self.total))
        self.progress = [received, self.total]
        QtGui.qApp.processEvents( )


class baseProgressWidget(QtGui.QWidget):
    def __init__(self, total, text='', parent=None):
        super(baseProgressWidget, self).__init__(parent)

        self.text  = text
        self.total = total
        self.progressbar = progressBar(self.total)
        self.progressbar.setTextVisible(True)

        self.bottomBorder = QtGui.QWidget( )
        self.bottomBorder.setStyleSheet("""
            background: palette(shadow);
        """)
        self.bottomBorder.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed))
        self.bottomBorder.setMinimumHeight(1)

        self.label  = QtGui.QLabel(self.text)
        self.label.setStyleSheet("""
            font-weight: bold;
        """)
        self.layout = QtGui.QVBoxLayout( )
        self.layout.setContentsMargins(10,0,10,0)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.progressbar)

        self.mainLayout = QtGui.QVBoxLayout( )
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.mainLayout.addLayout(self.layout)
        self.mainLayout.addWidget(self.bottomBorder)
        self.setLayout(self.mainLayout)


class downloadProgressWidget(baseProgressWidget):
    def __init__(self, total, text='', parent=None):
        super(downloadProgressWidget, self).__init__(total, text, parent)
        style ="""
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


class uploadProgressWidget(baseProgressWidget):
    def __init__(self, total, text, parent=None):
        super(uploadProgressWidget, self).__init__(total, text, parent)
        style ="""
        QProgressBar {
            border: 2px solid grey;
            border-radius: 5px;
            text-align: center;
        }

        QProgressBar::chunk {
            background-color: #60B9CE;
            width: 20px;
        }"""
        self.progressbar.setStyleSheet(style)


class progressDialog(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(progressDialog, self).__init__(parent)
        self.resize(400, 250)
        self.scrollArea = QtGui.QScrollArea( )
        self.scrollArea.setWidgetResizable(True)
        self.setCentralWidget(self.scrollArea)

        self.centralWidget = QtGui.QWidget( )
        self.scrollArea.setWidget(self.centralWidget)

        self.layout = QtGui.QVBoxLayout( )
        self.layout.setContentsMargins(0,0,0,0)
        self.centralWidget.setLayout(self.layout)
        self.show( )
        self.activateWindow()

    def addProgressbar(self, progressbar):
        self.layout.addWidget(progressbar)


def loginDialog(parent=None):
    login = LoginDialog(parent)
    if not login.isAccepted:
        return False
    elif login.visitorRadio.isChecked( ):
        return ('anonymous@', 'anonymous@', True)
    else:
        return (str(login.nameEdit.text( )), str(login.passwordEdit.text( )), True)

if __name__ == '__main__':
    def testLoinDialog( ):
        app = QtGui.QApplication([])
        print(loginDialog( ))

    def testProgressDialog( ):
        import random
        number = [x for x in range(1, 101)]
        progresses = [ ]
        while len(progresses) <= 20: progresses.append(random.choice(number))
        app = QtGui.QApplication([])
        w = progressDialog( )
        for i in progresses:
            pb = downloadProgressWidget(total=100, text='download')
            pb.progressbar.updateProgress(i)
            w.addProgressbar(pb)

        progresses.reverse( )
        for i in progresses:
            pb = uploadProgressWidget(total=100, text='upload')
            pb.progressbar.updateProgress(i)
            w.addProgressbar(pb)
        w.show( )
        app.exec_( )
    testLoinDialog( )
    testProgressDialog( )