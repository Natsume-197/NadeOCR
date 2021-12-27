import os
from tkinter.constants import FALSE
import cv2
import sys
import io
import numpy as np
from os import path
import tkinter as tk
import pyperclip as pc
from PIL import ImageGrab
from PyQt5.QtGui import QIcon
from google.cloud import vision
import simpleaudio as sa
from google.oauth2 import service_account
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu
import toast
from time import sleep
from PyQt5.QtCore import Qt
import configparser

class App:
    def __init__(self):
        self.app = QApplication(sys.argv)

        # Initil value obtained from config file for isSplit   

        icon = QIcon('./Resources/icon.png')
        menu = QMenu()

        self.scanAction = menu.addAction('Escanear')
        self.scanAction.triggered.connect(self.crop)

        self.splitAction = menu.addAction('Modo Texthooker')
        self.splitAction.setCheckable(True)
        self.splitAction.triggered.connect(self.split)
        self.splitAction.setChecked(to_bool(dict_config["isSplit"]))
        
        self.mangaAction = menu.addAction('Modo manga')
        self.mangaAction.setCheckable(True)
        self.mangaAction.triggered.connect(self.manga)
        self.mangaAction.setChecked(to_bool(dict_config["isManga"]))

        exitAction = menu.addAction('Salir')
        exitAction.triggered.connect(sys.exit)

        self.trayIcon = QSystemTrayIcon()
        self.trayIcon.setIcon(icon)
        self.trayIcon.setContextMenu(menu)
        self.trayIcon.setToolTip('NatsuOCR')

        self.trayIcon.activated.connect(self.onTrayIconActivated)

        self.trayIcon.show()
    
    def onTrayIconActivated(self, reason):
      if reason == QSystemTrayIcon.DoubleClick:
          self.scanAction.trigger()

    def run(self):
        self.app.exec_()
        sys.exit()

    def split(self):
        editConfig('user_settings', 'isSplit', str(self.splitAction.isChecked()))

    def manga(self):
        editConfig('user_settings', 'isManga', str(self.mangaAction.isChecked()))
    
    def crop(self):
        self.window = MyWidget()
        self.window.show()
        self.app.setQuitOnLastWindowClosed(False)

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.SubWindow )
        self.setWindowState(Qt.WindowMaximized | Qt.WindowFullScreen)
        root = tk.Tk()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setWindowTitle(' ')
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.setStyleSheet('''
            MyWidget { 
                background: black;
            }
        ''')
        self.setWindowOpacity(0.3)
        QtWidgets.QApplication.setOverrideCursor(
            QtGui.QCursor(QtCore.Qt.CrossCursor)
        )
        self.w = toast.W()
        self.show()

    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        qp.setPen(QtGui.QPen(QtGui.QColor('black'), 3))
        qp.setBrush(QtGui.QColor(255, 255, 255, 128))
        qp.drawRect(QtCore.QRect(self.begin, self.end))

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def scan(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        creds = service_account.Credentials.from_service_account_file(dir_path+'/credentials_google.json')

        """Detects text in the file."""
        path = dir_path+'/Images/capture.png'
        client = vision.ImageAnnotatorClient(
            credentials=creds,
        )
        with io.open(path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        response = client.text_detection(image=image)
        texts = response.text_annotations
        sentences = []
            
        dict_config2 = readConfig()
        isSplit = to_bool(dict_config2["isSplit"])

        try:
            sentences = texts[0].description.splitlines()
            if(isSplit == True):
                for i in range(len(sentences)):
                    sleep(0.3)
                    pc.copy(sentences[i])
            else:
                pc.copy(texts[0].description)
            
            wave_obj = sa.WaveObject.from_wave_file(dir_path+'/Resources/sfx-success1.wav')
            play_obj = wave_obj.play()
            self.w.showToaster()

        except Exception as error:
            print(error)
        if response.error.message:
            raise Exception(
                '{}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors'.format(
                    response.error.message))
    
    def mouseReleaseEvent(self, event):
        self.close()
        while QApplication.overrideCursor() is not None:
            QApplication.restoreOverrideCursor()
        x1 = min(self.begin.x(), self.end.x())
        y1 = min(self.begin.y(), self.end.y())
        x2 = max(self.begin.x(), self.end.x())
        y2 = max(self.begin.y(), self.end.y())

        img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        abspath = os.path.abspath(sys.argv[0])
        dname = os.path.dirname(abspath)
        if path.isfile('Images') == False:
            os.makedirs(dname + '\\Images', exist_ok=True)
        os.chdir(dname + "\\Images")
        list = os.listdir(dname + '\\Images')
        number_files = len(list)
        captureNum = number_files
        # img.save('capture ' + str(captureNum) + '.png')
        try:
            img.save('capture.png')
            img = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
            self.scan()
        except:
            print('Recorte no válido.')

def to_bool(value):
    if str(value).lower() in ("yes", "y", "true",  "t", "1"): return True
    if str(value).lower() in ("no",  "n", "false", "f", "0", "0.0", "", "none", "[]", "{}"): return False
    raise Exception('Invalid value for boolean conversion: ' + str(value))

def readConfig():
    parser = configparser.ConfigParser()
    abspath = os.path.abspath(sys.argv[0])
    dname = os.path.dirname(abspath)
    path_config = dname+'/config.ini'
    parser.read(path_config)
    isSplit = parser.get('user_settings', 'isSplit')
    isManga = parser.get('user_settings', 'isManga')
    dict_config = {
        "isSplit": isSplit,
        "isManga": isManga
    }
    return dict_config

def editConfig(section, option, value):
    parser = configparser.ConfigParser()
    abspath = os.path.abspath(sys.argv[0])
    dname = os.path.dirname(abspath)
    path_config = dname+'/config.ini'
    parser.read(path_config)

    with open(path_config, 'w') as configfile:
        parser.set(section, option, value)
        parser.write(configfile)

dict_config = readConfig()

if __name__ == "__main__":
    try:
        app = App()
        app.run()
    except Exception as e:
        file1 = open("log.txt","w")
        file1.write(str(e))
        file1.close()
