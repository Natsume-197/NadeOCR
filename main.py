import os
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

class App:
    def __init__(self):
        self.app = QApplication(sys.argv)
        icon = QIcon('./Resources/icon.png')
        menu = QMenu()

        self.scanAction = menu.addAction('Escanear')
        self.scanAction.triggered.connect(self.crop)
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

    def crop(self):
        self.window = MyWidget()
        self.window.show()
        self.app.setQuitOnLastWindowClosed(False)

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        root = tk.Tk()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setWindowTitle(' ')
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.setWindowOpacity(0.3)
        QtWidgets.QApplication.setOverrideCursor(
            QtGui.QCursor(QtCore.Qt.CrossCursor)
        )
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.w = toast.W()
        self.show()

    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        qp.setPen(QtGui.QPen(QtGui.QColor('black'), 3))
        qp.setBrush(QtGui.QColor(128, 128, 255, 128))
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
        try:
            print(texts[0].description)
            pc.copy(texts[0].description)
            wave_obj = sa.WaveObject.from_wave_file(dir_path+'/Resources/sfx-success1.wav')
            play_obj = wave_obj.play()
            self.w.showToaster()

        except Exception as error:
            print(error)
            print("No se encontro texto")
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

if __name__ == "__main__":
  app = App()
  app.run()
