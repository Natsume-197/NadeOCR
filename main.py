import io
import os
import sys
import cv2
import warnings
import keyboard
import numpy as np
import configparser
from os import path
import tkinter as tk
from time import sleep
import pyperclip as pc
from PIL import ImageGrab
from google.cloud import vision
from google.oauth2 import service_account
from PySide6.QtCore import Signal, QObject
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtGui import QIcon, QActionGroup, QAction, Qt, QKeySequence
from PySide6.QtWidgets import QSystemTrayIcon, QApplication, QWidget, QMenu, QTextEdit

warnings.filterwarnings("ignore", category=DeprecationWarning) 

# Config file reading and writing
def readConfig():
    parser = configparser.ConfigParser()
    abspath = os.path.abspath(sys.argv[0])
    dname = os.path.dirname(abspath)
    path_config = dname+'/config.ini'
    
    parser.read(path_config)
    
    isSplit = parser.get('user_settings', 'split_lines')
    removeNewLine = parser.get('user_settings', 'remove_new_line')
    shortcutKey = parser.get('user_settings', 'shortcut_key')
    
    dict_config = {
        "split_lines": isSplit,
        "remove_new_line": removeNewLine,
        "shortcut_key": shortcutKey
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

def to_bool(value):
    if str(value).lower() in ("yes", "y", "true",  "t", "1"): return True
    if str(value).lower() in ("no",  "n", "false", "f", "0", "0.0", "", "none", "[]", "{}"): return False
    raise Exception('Invalid value for boolean conversion: ' + str(value))

dict_config = readConfig()
shortcut_key = dict_config["shortcut_key"]
record_listener = []

# Listener for keyboard events using PySide6 and Signal
class KeyBoardManager(QObject):
    F1Signal = Signal()
    
    def start(self):
        keyboard.add_hotkey(shortcut_key, self.F1Signal.emit, suppress=True)
        
# Handles the GUI of the tray app when is used in background
class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        self.event_scan_click = None
        self.event_pause_click = None
        self.event_exit_click = None
        self.is_actived = True

        QSystemTrayIcon.__init__(self)
        self.setIcon(icon)

        menu = QMenu(parent)  
                      
        # Actions Available in the Menu
        self._scan_action = menu.addAction("Escanear", self.on_scan_click)
        
        menu.addSeparator()
        
        normal_mode_action = QAction("Modo Normal", None, checkable=True)
        # manga_mode_action = QAction("Modo Manga", None, checkable=True)
        action_group = QActionGroup(self)
        action_group.addAction(normal_mode_action)
        # action_group.addAction(manga_mode_action)
        normal_mode_action.setChecked(True)
        menu.addActions(action_group.actions())
        
        menu.addSeparator()
        
        self.split_copy_action = menu.addAction("Copiar línea por línea", None)
        self.split_copy_action.setCheckable(True)
        self.split_copy_action.setChecked(to_bool(dict_config["split_lines"]))
        self.split_copy_action.triggered.connect(self.split)
        
        self.split_remove_nl_action = menu.addAction("Remover salto de línea", None)
        self.split_remove_nl_action.setCheckable(True)
        self.split_remove_nl_action.setChecked(to_bool(dict_config["remove_new_line"]))
        self.split_remove_nl_action.triggered.connect(self.remove_new_line)
        
        menu.addSeparator()
        
        self.history = menu.addAction("Historial", self.record_click)
        self._exit_action = menu.addAction("Salir", self.on_exit_click)

        self.setContextMenu(menu)
        
        # Extra configuration
        self.setToolTip('NadeOCR')
        self.activated.connect(self.on_icon_click)
        self.show()
        
        # Shortcut configuration for the actions
        self.manager = KeyBoardManager()
        self.manager.F1Signal.connect(self.on_scan_click)
        self._scan_action.setShortcut(QKeySequence(shortcut_key))
        self.manager.start()
                
    # Methods used for the actions available in the menu 
    def on_scan_click(self):
        self.fire_scan_click()
        self.window = MyWidget()
        self.window.show()
        #self.setIcon(QIcon("playing.svg"))  

    def on_exit_click(self):
        self.fire_exit_click()
        exit(0)

    def on_icon_click(self, reason):
        # if reason == self.DoubleClick:
        #     # newicon = QIcon("blocked.svg")
        #     self.setIcon(QIcon("blocked.svg"))
        if reason == self.DoubleClick:
            self.on_scan_click()     

    def fire_scan_click(self):
        if self.event_scan_click:
            self.event_scan_click(self)

    def fire_exit_click(self):
        if self.event_exit_click:
            self.event_exit_click(self)
            
    def record_click(self):
        self.window_record = RecordWindow()
    
    def split(self):
        editConfig('user_settings', 'split_lines', str(self.split_copy_action.isChecked()))

    def remove_new_line(self):
        editConfig('user_settings', 'remove_new_line', str(self.split_remove_nl_action.isChecked()))

# Widged that handles the croping of the image at real time and scanning
class MyWidget(QWidget):
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
    
    # Scanning action using Google API VISION
    def scan(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        creds = service_account.Credentials.from_service_account_file(dir_path+'/credentials_google.json')

        path = dir_path+'/Resources/Images/capture.png'
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
        isSplit = to_bool(dict_config2["split_lines"])
        
        removeNewLine = to_bool(dict_config2["remove_new_line"])
        
        try:
            if (removeNewLine == True):
                result = texts[0].description.replace("\n", " ")
                record_listener.append(result)
            else:
                result = texts[0].description
                record_listener.append(result)
            
            if(isSplit == True):
                sentences = texts[0].description.splitlines()
                for i in range(len(sentences)):
                    sleep(0.3)
                    pc.copy(sentences[i])
                    print(sentences[i])
            else:
                pc.copy(result)
                print(result)
                        
        except Exception as error:
            print(error)
        if response.error.message:
            raise Exception(
                '{}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors'.format(
                    response.error.message))
            
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

        resources_images_dir = os.path.join(dname, "Resources", "Images")
        if not path.isfile(resources_images_dir):
            os.makedirs(resources_images_dir, exist_ok=True)

        try:
            img.save(os.path.join(resources_images_dir, 'capture.png'))
            img = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
            self.scan()
        except Exception as error:
            print(error)

class RecordWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Historial")

        # Set vertical layout
        self.setLayout(QtWidgets.QVBoxLayout())
        
        # Create a label
        label_record = QtWidgets.QLabel("Historial de escaneos")
        label_record.setFont(QtGui.QFont("Arial", 20))
        self.layout().addWidget(label_record)
        
        # Create a text box
        self.text_box = QTextEdit(self, 
            lineWrapMode=QTextEdit.FixedColumnWidth, 
            lineWrapColumnOrWidth=50,
            placeholderText = "No hay un historial disponible",
            readOnly=False,
        )
        
        self.layout().addWidget(self.text_box)
        
        
        self.show()

        self.update_text()
        
                
    def update_text(self):
        for index, value in enumerate(record_listener):
            record_listener[index] =  value
            
        myString = '\n\n'.join(map(str, record_listener))
        self.text_box.setText(myString)    
              
class SystemTrayApp:
    def __init__(self):
        self.event_exit_app = None
        self._app = QApplication(sys.argv)
        self._widget = QWidget()
        self._icon = SystemTrayIcon(QIcon("./Resources/Assets/icon.ico"), self._widget)
        self._icon.event_exit_click = self.on_exit_click
        
    def run(self):
        sys.exit(self._app.exec())

    def fire_exit_app(self):
        if self.event_exit_app:
            self.event_exit_app(self)

    def on_exit_click(self, sender):
        self.fire_exit_app()

if __name__ == '__main__':
    app = SystemTrayApp()
    QApplication.setQuitOnLastWindowClosed(False) # Keep the app running after the last window closed
    app.run()   
    
