import os
import sys
import cv2
import numpy as np
from os import path
import tkinter as tk
from PIL import ImageGrab
from PySide6.QtGui import Qt
from PySide6 import QtCore, QtGui
from PySide6.QtWidgets import QWidget, QApplication
from GUI.functions.google_provider import GoogleProvider
from GUI.functions.utils.extra import read_config_ini
from GUI.functions.easyocr_provider import EasyOCRProvider

class CropWidget(QWidget): 
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.SubWindow )
        self.showFullScreen()
        root = tk.Tk()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setWindowTitle(' ')

        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.setStyleSheet('''
            CropWidget { 
                background: black;
            }
        ''')
        self.setWindowOpacity(0.3)
        self.show()
        self.setCursor(QtGui.QCursor(Qt.CrossCursor))
    
    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        qp.setPen(QtGui.QPen(QtGui.QColor('white'), 2))
        qp.setBrush(QtGui.QColor(255, 255, 255, 128))
        qp.drawRect(QtCore.QRect(self.begin, self.end))

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()
        
    def mouseReleaseEvent(self, event):
        self.hide()
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

        resources_images_dir = os.path.join(dname, "resources", "temp")
        if not path.isfile(resources_images_dir):
            os.makedirs(resources_images_dir, exist_ok=True)

        try:
            img.save(os.path.join(resources_images_dir, 'capture.png'))
            img = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)  
            
            config_reader = read_config_ini()
            ocr_provider = config_reader["provider_settings"]["ocr_provider"]
            
            if(ocr_provider == "Google"):   
                GoogleProvider.scan_google()
            elif(ocr_provider == "Tesseract"):
                print("Tesseract")
            elif(ocr_provider == "EasyOCR"):
                EasyOCRProvider.scan_easyocr()
            
        except Exception as error:
            print(error)