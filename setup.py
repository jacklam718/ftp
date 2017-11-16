import os
from setuptools import setup

APP = ['ftp_client.py']
APP_NAME = 'PyQt FTP Client'
DATA_FILES = [
    os.path.join(os.path.dirname(__file__), 'icons/home.png'),
    os.path.join(os.path.dirname(__file__), 'icons/back.png'),
    os.path.join(os.path.dirname(__file__), 'icons/next.png'),
    os.path.join(os.path.dirname(__file__), 'icons/upload.png'),
    os.path.join(os.path.dirname(__file__), 'icons/connect.png'),
    os.path.join(os.path.dirname(__file__), 'icons/download.png'),
    os.path.join(os.path.dirname(__file__), 'icons/internet.png'),
    os.path.join(os.path.dirname(__file__), 'icons/folder.png'),
    os.path.join(os.path.dirname(__file__), 'icons/file.png'),
]
# OPTIONS = {'argv_emulation': True}
OPTIONS = {
    'argv_emulation': True,
    'includes': ['sip', 'PyQt4']
}

setup(
    app=APP,
    name=APP_NAME,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
