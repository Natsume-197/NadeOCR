import os
import sys
from os import path
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel
from GUI.functions.utils.extra import read_config_ini
from GUI.functions.google_provider import GoogleProvider
from GUI.functions.mangaocr_provider import MangaOcrProvider

class CropWidget(QWidget): 
    def __init__(self, parent):
        super().__init__()
        self.parent = parent 

        # Basic configuration
        self.setWindowTitle(' ')
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)   
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.SubWindow )
        self.setWindowState(Qt.WindowMaximized | Qt.WindowFullScreen)    
        self.setStyleSheet("background:transparent;")
        self.setCursor(QtGui.QCursor(Qt.CrossCursor))

        # Crop border personalization
        self.outsideSquareColor = "white"
        self.squareThickness = 3

        # Coords variables
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()

        self.showFullScreen()

    def paintEvent(self, event):
        trans = QtGui.QColor(0, 0, 0, 200)
        r = QtCore.QRectF(self.begin, self.end).normalized()

        qp = QtGui.QPainter(self)
        trans.setAlphaF(0.2)
        qp.setBrush(trans)
        outer = QtGui.QPainterPath()
        outer.addRect(QtCore.QRectF(self.rect()))
        inner = QtGui.QPainterPath()
        inner.addRect(r)
        r_path = outer - inner
        qp.drawPath(r_path)

        qp.setPen(
            QtGui.QPen(QtGui.QColor(self.outsideSquareColor), self.squareThickness)
        )
        trans.setAlphaF(0)
        qp.setBrush(trans)
        qp.drawRect(r)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self.end = event.pos()
        self.update()
        
    def mouseReleaseEvent(self, event):
        self.close()
        QtCore.QTimer.singleShot(1000, self.screenshot)
        
    def screenshot(self):
        screen = QtGui.QGuiApplication.primaryScreen()
        window = self.windowHandle()
        if window is not None:
            screen = window.screen()
        if screen is None:
            print("failed")
            return

        original_pixmap = screen.grabWindow(0)
        output_pixmap = original_pixmap.copy(
            QtCore.QRect(self.begin, self.end).normalized()
        )

        #self.label = QLabel(pixmap=output_pixmap)
        #self.label.show()

        abspath = os.path.abspath(sys.argv[0])
        dname = os.path.dirname(abspath)
        resources_images_dir = os.path.join(dname, "resources", "temp")

        if not path.isfile(resources_images_dir):
            os.makedirs(resources_images_dir, exist_ok=True)

        try:
            # Saving temp image in resources/temp
            output_pixmap.save(os.path.join(resources_images_dir, "capture.png"))
            
            # Provider selection 
            config_reader = read_config_ini()
            ocr_provider = config_reader["provider_settings"]["ocr_provider"]
            if(ocr_provider == "Google"):   
                GoogleProvider.scan_google(self)
            elif(ocr_provider == "MangaOCR"):
                MangaOcrProvider.scan_mangaocr(self)
            
        except Exception as error:
            print(error)