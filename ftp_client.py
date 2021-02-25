#!/usr/bin/env python
#--*--encoding:utf8--*--
import os
import sys
from threading import Thread
from ftplib import FTP
from urllib.parse import urlparse
import tomlkit
from utils import fileProperty
from dialog import loginDialog, ProgressDialog, DownloadProgressWidget, UploadProgressWidget
from permissions import FilePerm
from humanbytes import HumanBytes

from PyQt5 import uic, QtWidgets, QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

project_directory = os.path.abspath(os.path.dirname(sys.argv[0]))
home_directory = os.path.expanduser('~')

app_icon_path = os.path.join(os.path.dirname(__file__), 'icons')
qIcon = lambda name: QtGui.QIcon(os.path.join(app_icon_path, name))

QApplication.setApplicationName("FTP")
#QApplication.setOrganizationName("WizardAssistant")
#QApplication.setOrganizationDomain("wizardassistant.com")

# ---------------------------------------------------------------------------------#
## The BaseGuiWidget provide LocalGuiWidget and RemoteGuiWidget to inheritance,  ##
## because this program has main of two widgets, local and remote file list with ##
## control widget, they are similar interface, so I write the superclass         ##
# ---------------------------------------------------------------------------------#
class BaseGuiWidget(QWidget):
    def __init__(self, parent=None):
        super(BaseGuiWidget, self).__init__(parent)
        self.resize(600, 600)
        self.createFileListWidget()
        self.createGroupboxWidget()

        # setting column width
        for pos, width in enumerate((150, 70, 70, 70, 90, 90)):
            self.fileList.setColumnWidth(pos, width)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.groupBox)
        self.mainLayout.addWidget(self.fileList)
        # self.mainLayout.setMargin(5)
        self.setLayout(self.mainLayout)
        self.setWindowTitle(QApplication.applicationName() + " v" + version)

        # completer for path edit
        completer = QCompleter()
        self.completerModel = QStringListModel()
        completer.setModel(self.completerModel)
        self.pathEdit.setCompleter(completer)
        # Custom context menu
        self.fileList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.fileList.customContextMenuRequested.connect(self.menu_context_tree)

    def createGroupboxWidget(self):
        self.pathEdit = QLineEdit()
        self.homeButton = QPushButton()
        self.backButton = QPushButton()
        self.nextButton = QPushButton()
        self.homeButton.setIcon(qIcon('home.png'))
        self.backButton.setIcon(qIcon('back.png'))
        self.nextButton.setIcon(qIcon('next.png'))
        self.homeButton.setIconSize(QSize(20, 20))
        self.homeButton.setEnabled(False)
        self.backButton.setEnabled(False)
        self.nextButton.setEnabled(False)
        self.hbox1 = QHBoxLayout()
        self.hbox2 = QHBoxLayout()
        self.hbox1.addWidget(self.homeButton)
        self.hbox1.addWidget(self.pathEdit)
        self.hbox2.addWidget(self.backButton)
        self.hbox2.addWidget(self.nextButton)
        self.hbox2.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.gLayout = QVBoxLayout()
        self.gLayout.addLayout(self.hbox1)
        self.gLayout.addLayout(self.hbox2)
        self.gLayout.setSpacing(5)
        # self.gLayout.setMargin(5)
        self.groupBox = QGroupBox('Widgets')
        self.groupBox.setLayout(self.gLayout)

    def createFileListWidget(self):
        self.fileList = QTreeWidget()
        self.fileList.setIconSize(QSize(20, 20))
        self.fileList.setRootIsDecorated(False)
        self.fileList.setHeaderLabels(('Name', 'Size', 'Owner', 'Group', 'Time', 'Mode'))
        self.fileList.header().setStretchLastSection(True)
        self.fileList.setSortingEnabled(True)
        #self.fileList.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        # self.fileList.setTreePosition(0)
        # if not self.fileList.currentItem():
        #     self.fileList.setCurrentItem(self.fileList.topLevelItem(0))
        #     self.fileList.setEnabled(True)
        # Connect the contextmenu

    def menu_context_tree(self, point):
        # Infos about the node selected.
        index = self.fileList.indexAt(point)

        if not index.isValid():
            return

        item = self.fileList.itemAt(point)
        name = item.text(0)  # The text of the node.

        # We build the menu.
        menu = QMenu()
        action = menu.addAction("Mouse above")
        # action = menu.addAction(name)
        menu.addSeparator()
        action_1 = menu.addAction("Change Permissions")
        action_2 = menu.addAction("File information")
        action_3 = menu.addAction("Copy File Path")


class LocalGuiWidget(BaseGuiWidget):
    def __init__(self, parent=None):
        BaseGuiWidget.__init__(self, parent)
        self.uploadButton = QPushButton()
        self.connectButton = QPushButton()
        self.uploadButton.setIcon(qIcon('upload.png'))
        self.connectButton.setIcon(qIcon('connect.png'))
        self.hbox2.addWidget(self.uploadButton)
        self.hbox2.addWidget(self.connectButton)
        self.groupBox.setTitle('Local')


class RemoteGuiWidget(BaseGuiWidget):
    def __init__(self, parent=None):
        BaseGuiWidget.__init__(self, parent)
        self.downloadButton = QPushButton()
        self.downloadButton.setIcon(qIcon('download.png'))
        self.homeButton.setIcon(qIcon('internet.png'))
        self.hbox2.addWidget(self.downloadButton)
        self.groupBox.setTitle('Remote')


class FtpClient(QWidget):
    def __init__(self, parent=None):
        super(FtpClient, self).__init__(parent)
        self.ftp = FTP()
        self.setupGui()
        self.downloads = []
        self.localBrowseRec = []
        self.remoteBrowseRec = []
        self.local_pwd = os.getenv('HOME')
        self.ftp_hostname = ''
        self.ftp_username = ''
        self.ftp_password = ''
        # self.ftp_hostname = os.getenv('ftp_hostname')
        # self.ftp_username = os.getenv('ftp_username')
        # self.ftp_password = os.getenv('ftp_password')

        self.local.pathEdit.setText(self.local_pwd)
        self.localOriginPath = self.local_pwd
        self.localBrowseRec.append(self.local_pwd)
        self.loadToLocalFileList()

        # Signals
        self.remote.homeButton.clicked.connect(self.cdToRemoteHomeDirectory)
        self.remote.fileList.itemDoubleClicked.connect(self.cdToRemoteDirectory)
        self.remote.fileList.itemClicked.connect(lambda: self.remote.downloadButton.setEnabled(True))
        self.remote.backButton.clicked.connect(self.cdToRemoteBackDirectory)
        self.remote.nextButton.clicked.connect(self.cdToRemoteNextDirectory)
        self.remote.downloadButton.clicked.connect(lambda: Thread(target=self.download).start())
        # QObject.connect(self.remote.pathEdit, pyqtSignal('returnPressed( )'), self.cdToRemotePath)
        self.remote.pathEdit.returnPressed.connect(self.cdToRemotePath)

        self.local.homeButton.clicked.connect(self.cdToLocalHomeDirectory)
        self.local.fileList.itemDoubleClicked.connect(self.cdToLocalDirectory)
        self.local.fileList.itemClicked.connect(lambda: self.local.uploadButton.setEnabled(True))
        self.local.backButton.clicked.connect(self.cdToLocalBackDirectory)
        self.local.nextButton.clicked.connect(self.cdToLocalNextDirectory)
        self.local.uploadButton.clicked.connect(lambda: Thread(target=self.upload).start())
        self.local.connectButton.clicked.connect(self.connect)
        # QObject.connect(self.local.pathEdit, pyqtSignal('returnPressed( )'), self.cdToLocalPath)
        self.local.pathEdit.returnPressed.connect(self.cdToLocalPath)

        self.progressDialog = ProgressDialog(self)

    def setupGui(self):
        self.resize(1200, 650)
        self.local = LocalGuiWidget(self)
        self.remote = RemoteGuiWidget(self)
        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.remote)
        mainLayout.addWidget(self.local)
        mainLayout.setSpacing(0)
        # mainLayout.setMargin(5)
        self.setLayout(mainLayout)

    def initialize(self):
        # self.localBrowseRec = []
        # self.remoteBrowseRec = []
        self.pwd = self.ftp.pwd()

        # self.local_pwd = os.getenv('HOME')
        self.remoteOriginPath = self.pwd
        # self.localOriginPath = self.local_pwd
        # self.localBrowseRec.append(self.local_pwd)
        self.remoteBrowseRec.append(self.pwd)
        self.downloadToRemoteFileList()
        # self.loadToLocaFileList()

    def disconnect(self):
        pass

    def connect(self):
        if not bool(self.ftp_hostname):
            try:
                from urlparse import urlparse
            except ImportError:
                from urllib.parse import urlparse

            result = QInputDialog.getText(self, 'Connect To Host', 'Host Address', QLineEdit.Normal)
            if not result[1]:
                return
            try:
                self.ftp_hostname = str(result[0])
            except AttributeError:
                self.ftp_hostname = str(result[0])

        try:
            if self.ftp_hostname:
                self.ftp.connect(host=self.ftp_hostname, port=21, timeout=10)
            else:
                self.ftp.connect(host=self.ftp_hostname, port=21, timeout=10)
            self.login()
        except Exception as error:
            raise error

    def login(self):
        # if not bool(self.ftp_username) or bool(self.ftp_password):
        ask = loginDialog(self)
        if not ask:
                 return
        else:
             self.ftp_username, self.ftp_password = ask[:2]

        # self.ftp.user = self.ftp_username
        # self.ftp.passwd = self.ftp_password
        self.ftp.login(user=self.ftp_username, passwd=self.ftp_password)
        self.initialize()
        self.remote.pathEdit.setText(self.pwd)

    '''
    def connect(self, address, port=21, timeout=10):
        from urlparse import urlparse
        if urlparse(address).hostname:
            self.ftp.connect(urlparse(address).hostname, port, timeout)
        else:
            self.ftp.connect(address, port, timeout)

    def login(self, name=None, passwd=None):
        if not name:
            self.ftp.login( )
        else:
            self.ftp.login(name, passwd)
            self.ftp.user, self.ftp.passwd = (user, passwd)
        self.initialize( )
    '''

    # ---------------------------------------------------------------------------------#
    ## the downloadToRemoteFileList with loadToLocalFileList is doing the same thing ##
    # ---------------------------------------------------------------------------------#
    def downloadToRemoteFileList(self):
        """
        download file and directory list from FTP Server
        """
        self.remoteWordList = []
        self.remoteDir = {}
        self.ftp.dir('.', self.addItemToRemoteFileList)
        self.remote.completerModel.setStringList(self.remoteWordList)
        self.remote.fileList.sortByColumn(0, Qt.SortOrder.AscendingOrder)

    def loadToLocalFileList(self):
        """
        load file and directory list from local computer
        """
        self.localWordList = []
        self.localDir = {}
        for f in os.listdir(self.local_pwd):
            pathname = os.path.join(self.local_pwd, f)
            self.addItemToLocalFileList(fileProperty(pathname))
        self.local.completerModel.setStringList(self.localWordList)
        self.local.fileList.sortByColumn(0, Qt.SortOrder.AscendingOrder)


    def addItemToRemoteFileList(self, content):
        mode, num, owner, group, filesize_human, date, filename, size = self.parseFileInfo(content)
        if content.startswith('d'):
            icon = qIcon('folder.png')
            pathname = os.path.join(self.pwd, filename)
            self.remoteDir[pathname] = True
            self.remoteWordList.append(filename)

        else:
            icon = qIcon('file.png')

        item = QTreeWidgetItem()
        item.setIcon(0, icon)
        for n, i in enumerate((filename, filesize_human, owner, group, date, mode, size)):
            item.setText(n, i)

        self.remote.fileList.addTopLevelItem(item)
        if not self.remote.fileList.currentItem():
            self.remote.fileList.setCurrentItem(self.remote.fileList.topLevelItem(0))
            self.remote.fileList.setEnabled(True)


    def addItemToLocalFileList(self, content):
        mode, num, owner, group, filesize_human, date, filename, size = self.parseFileInfo(content)
        if content.startswith('d'):
            icon = qIcon('folder.png')
            pathname = os.path.join(self.local_pwd, filename)
            self.localDir[pathname] = True
            self.localWordList.append(filename)

        else:
            icon = qIcon('file.png')

        item = QTreeWidgetItem()
        item.setIcon(0, icon)
        for n, i in enumerate((filename, filesize_human, owner, group, date, mode, size)):
            # print((filename, size, owner, group, date, mode))
            item.setText(n, i)
        self.local.fileList.addTopLevelItem(item)
        if not self.local.fileList.currentItem():
            self.local.fileList.setCurrentItem(self.local.fileList.topLevelItem(0))
            self.local.fileList.setEnabled(True)

    def parseFileInfo(self, file):
        """
        parse files information "drwxr-xr-x 2 root wheel 1024 Nov 17 1993 lib" result like follower
                                "drwxr-xr-x", "2", "root", "wheel", "1024 Nov 17 1993", "lib"
        """
        item = [f for f in file.split(' ') if f != '']
        mode, num, owner, group, size, date, filename = (
            item[0], item[1], item[2], item[3], item[4], ' '.join(item[5:8]), ' '.join(item[8:]))
        filesize_human = HumanBytes.format(int(size), precision=2)
        return mode, num, owner, group, filesize_human, date, filename, size

    # --------------------------#
    ## for remote file system ##
    # --------------------------#
    def cdToRemotePath(self):
        try:
            pathname = str(self.remote.pathEdit.text())
        except AttributeError:
            pathname = str(self.remote.pathEdit.text())
        try:
            self.ftp.cwd(pathname)
        except:
            return
        self.cwd = pathname.startswith(os.path.sep) and pathname or os.path.join(self.pwd, pathname)
        self.updateRemoteFileList()
        self.remote.pathEdit.setText(self.cwd)
        self.remote.backButton.setEnabled(True)
        if os.path.abspath(pathname) != self.remoteOriginPath:
            self.remote.homeButton.setEnabled(True)
        else:
            self.remote.homeButton.setEnabled(False)

    def cdToRemoteDirectory(self, item, column):
        pathname = os.path.join(self.pwd, str(item.text(0)))
        if not self.isRemoteDir(pathname):
            return
        self.remoteBrowseRec.append(pathname)
        self.ftp.cwd(pathname)
        self.pwd = self.ftp.pwd()
        self.remote.pathEdit.setText(self.pwd)
        self.updateRemoteFileList()
        self.remote.backButton.setEnabled(True)
        if pathname != self.remoteOriginPath:
            self.remote.homeButton.setEnabled(True)

    def cdToRemoteBackDirectory(self):
        pathname = self.remoteBrowseRec[self.remoteBrowseRec.index(self.pwd) - 1]
        if pathname != self.remoteBrowseRec[0]:
            self.remote.backButton.setEnabled(True)
        else:
            self.remote.backButton.setEnabled(False)

        if pathname != self.remoteOriginPath:
            self.remote.homeButton.setEnabled(True)
        else:
            self.remote.homeButton.setEnabled(False)
        self.remote.nextButton.setEnabled(True)
        self.pwd = pathname
        self.ftp.cwd(pathname)
        self.updateRemoteFileList()
        self.remote.pathEdit.setText(self.pwd)

    def cdToRemoteNextDirectory(self):
        pathname = self.remoteBrowseRec[self.remoteBrowseRec.index(self.pwd) + 1]
        if pathname != self.remoteBrowseRec[-1]:
            self.remote.nextButton.setEnabled(True)
        else:
            self.remote.nextButton.setEnabled(False)
        self.remote.backButton.setEnabled(True)
        if pathname != self.remoteOriginPath:
            self.remote.homeButton.setEnabled(True)
        else:
            self.remote.homeButton.setEnabled(False)
        self.remote.backButton.setEnabled(True)
        self.pwd = pathname
        self.ftp.cwd(pathname)
        self.updateRemoteFileList()
        self.remote.pathEdit.setText(self.pwd)

    def cdToRemoteHomeDirectory(self):
        self.ftp.cwd(self.remoteOriginPath)
        self.pwd = self.remoteOriginPath
        self.updateRemoteFileList()
        self.remote.pathEdit.setText(self.pwd)
        self.remote.homeButton.setEnabled(False)

    # -------------------------#
    ## for local file system ##
    # -------------------------#
    def cdToLocalPath(self):
        try:
            pathname = str(self.local.pathEdit.text())
        except AttributeError:
            pathname = str(self.local.pathEdit.text())
        pathname = pathname.endswith(os.path.sep) and pathname or os.path.join(self.local_pwd, pathname)
        if not os.path.exists(pathname) and not os.path.isdir(pathname):
            return

        else:
            self.localBrowseRec.append(pathname)
            self.local_pwd = pathname
            self.updateLocalFileList()
            self.local.pathEdit.setText(self.local_pwd)
            self.local.backButton.setEnabled(True)
            print(pathname, self.localOriginPath)
            if os.path.abspath(pathname) != self.localOriginPath:
                self.local.homeButton.setEnabled(True)
            else:
                self.local.homeButton.setEnabled(False)

    def cdToLocalDirectory(self, item, column):
        pathname = os.path.join(self.local_pwd, str(item.text(0)))
        if not self.isLocalDir(pathname):
            return
        self.localBrowseRec.append(pathname)
        self.local_pwd = pathname
        self.updateLocalFileList()
        self.local.pathEdit.setText(self.local_pwd)
        self.local.backButton.setEnabled(True)
        if pathname != self.localOriginPath:
            self.local.homeButton.setEnabled(True)

    def cdToLocalBackDirectory(self):
        pathname = self.localBrowseRec[self.localBrowseRec.index(self.local_pwd) - 1]
        if pathname != self.localBrowseRec[0]:
            self.local.backButton.setEnabled(True)
        else:
            self.local.backButton.setEnabled(False)
        if pathname != self.localOriginPath:
            self.local.homeButton.setEnabled(True)
        else:
            self.local.homeButton.setEnabled(False)
        self.local.nextButton.setEnabled(True)
        self.local_pwd = pathname
        self.updateLocalFileList()
        self.local.pathEdit.setText(self.local_pwd)

    def cdToLocalNextDirectory(self):
        pathname = self.localBrowseRec[self.localBrowseRec.index(self.local_pwd) + 1]
        if pathname != self.localBrowseRec[-1]:
            self.local.nextButton.setEnabled(True)
        else:
            self.local.nextButton.setEnabled(False)
        if pathname != self.localOriginPath:
            self.local.homeButton.setEnabled(True)
        else:
            self.local.homeButton.setEnabled(False)
        self.local.backButton.setEnabled(True)
        self.local_pwd = pathname
        self.updateLocalFileList()
        self.local.pathEdit.setText(self.local_pwd)

    def cdToLocalHomeDirectory(self):
        self.local_pwd = self.localOriginPath
        self.updateLocalFileList()
        self.local.pathEdit.setText(self.local_pwd)
        self.local.homeButton.setEnabled(False)

    def updateLocalFileList(self):
        self.local.fileList.clear()
        self.loadToLocalFileList()

    def updateRemoteFileList(self):
        self.remote.fileList.clear()
        self.downloadToRemoteFileList()

    def isLocalDir(self, dirname):
        return self.localDir.get(dirname, None)

    def isRemoteDir(self, dirname):
        return self.remoteDir.get(dirname, None)

    def download(self):
        item = self.remote.fileList.currentItem()
        filesize = int(item.text(6))

        try:
            srcfile = os.path.join(self.pwd, str(item.text(0)))
            dstfile = os.path.join(self.local_pwd, str(item.text(0)))
        except AttributeError:
            srcfile = os.path.join(self.pwd, str(item.text(0)))
            dstfile = os.path.join(self.local_pwd, str(item.text(0)))

        pb = self.progressDialog.addProgress(
            type='download',
            title=srcfile,
            size=filesize,
        )

        def callback(data):
            pb.set_value(data)
            file.write(data)

        file = open(dstfile, 'wb')
        fp = FTP()
        fp.connect(host=self.ftp_hostname, port=self.ftp.port, timeout=self.ftp.timeout)
        fp.login(user=self.ftp_username, passwd=self.ftp_password)
        fp.retrbinary(cmd='RETR ' + srcfile, callback=callback)

    def upload(self):
        item = self.local.fileList.currentItem()
        print(item)
        # filesize = int(item.text(1))
        filesize = int(item.text(6))

        try:
            srcfile = os.path.join(self.local_pwd, str(item.text(0)))
            dstfile = os.path.join(self.pwd, str(item.text(0)))
        except AttributeError:
            srcfile = os.path.join(self.local_pwd, str(item.text(0)))
            dstfile = os.path.join(self.pwd, str(item.text(0)))

        pb = self.progressDialog.addProgress(
            type='upload',
            title=srcfile,
            size=filesize,
        )

        file = open(srcfile, 'rb')
        fp = FTP()
        fp.connect(host=self.ftp_hostname, port=self.ftp.port, timeout=self.ftp.timeout)
        fp.login(user=self.ftp_username, passwd=self.ftp_password)
        fp.storbinary(cmd='STOR ' + dstfile, fp=file, callback=pb.set_value)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = FtpClient()
    client.show()
    app.exec_()
