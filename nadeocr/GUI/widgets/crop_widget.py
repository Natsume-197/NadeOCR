import ctypes
import os
from os import path

from PIL import ImageGrab
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDesktopWidget, QWidget
from screeninfo import get_monitors

from nadeocr.GUI.functions.google_provider import GoogleProvider
from nadeocr.GUI.functions.mangaocr_provider import MangaOcrProvider
from nadeocr.GUI.functions.utils.extra import get_data, read_config_ini

_ROOT = os.path.abspath(os.path.dirname(__file__))


class CropWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        # Basic configuration
        self.setWindowTitle(" ")
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.SubWindow
        )
        self.setWindowState(Qt.WindowMaximized | Qt.WindowFullScreen)
        self.setStyleSheet("background:transparent;")
        self.setCursor(QtGui.QCursor(Qt.CrossCursor))

        # Crop border personalization
        self.outsideSquareColor = "white"
        self.squareThickness = 3

        # Coords variables
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
        topX = 0
        topY = 0
        self.x = 0
        self.y = 0

        # Support for multiple monitors by painting every screen
        desktop = QDesktopWidget()
        desktop_count = desktop.screenCount()

        for i in range(desktop_count):
            geo = desktop.screenGeometry(i)
            _x = geo.x()
            _y = geo.y()
            topX = _x if _x < topX else topX
            topY = _y if _y < topY else topY

        total_width = 0
        total_height = 0

        # Get total width and height for every available monitor
        for current in get_monitors():
            total_height += current.height
            total_width += current.width

        self.width = total_width
        self.height = total_height

        self.setGeometry(self.x, self.y, self.width, self.height)

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
        self.globalBegin = event.globalPos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self.end = event.pos()
        self.globalEnd = event.globalPos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.close()
        QtCore.QTimer.singleShot(1000, self.screenshot)

    def screenshot(self):

        try:
            x1 = min(self.globalBegin.x(), self.globalEnd.x())
            y1 = min(self.globalBegin.y(), self.globalEnd.y())
            x2 = max(self.globalBegin.x(), self.globalEnd.x())
            y2 = max(self.globalBegin.y(), self.globalEnd.y())
        except:
            print("No coords available")

        try:
            img = ImageGrab.grab(bbox=(x1, y1, x2, y2), all_screens=True)

        except:
            print("Unexpected error grabbing image")

        resources_images_dir = get_data(_ROOT, "./../../resources/temp", "")

        if not path.isfile(resources_images_dir):
            os.makedirs(resources_images_dir, exist_ok=True)

        try:
            # Saving temp image in resources/temp
            path_route = get_data(_ROOT, "./../../resources/temp", "capture.png")
            img.save(path_route)

            # Provider selection
            config_reader = read_config_ini()
            ocr_provider = config_reader["provider_settings"]["ocr_provider"]
            if ocr_provider == "Google":
                GoogleProvider.scan_google(self)
            elif ocr_provider == "MangaOCR":
                MangaOcrProvider.scan_mangaocr(self)

        except Exception as error:
            print(error)
