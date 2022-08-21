import sys
import platform
from PyQt5 import QtWidgets
from nadeocr.GUI.widgets.tray_widget import SystemTray
from PySide6.QtWidgets import QApplication 

class MainApp: 
    def __init__(self):
        # OS specific setup during application startup
        self.__os_specific_setup()
        # Keep the app running after the last window closed
        QApplication.setQuitOnLastWindowClosed(False) 
        # Main instance of NadeOCR
        self._app = QApplication(sys.argv)
        # Second instance with Tray System 
        self.tray_system = SystemTray()
        
    # Keeps the main process running until exit
    def run(self):
        sys.exit(self._app.exec())
        
    def __os_specific_setup(self):
        if platform.system() == "Windows":
            import ctypes
            # Assigning AppUserModelID in order to fix taskbar's icons for Windows
            id_app = 'natsume.nadeocr.0.5.0' 
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(id_app)
            # Fix for DPI scaling related with cropping and GUI in some machines 
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(2) # Windows version >= 8.1
            except:
                ctypes.windll.user32.SetProcessDPIAware() # Windows 8.0 or less 

def run(): 
    # PySide6/PyQT6 has a bug where mouse coordinates are wrong if DPI is higher than 125% on Windows machines
    # In order to fix it, I must use (temporaly) an instance of PyQT5 called app_crop
    # That way, snipping the screen works as expected
    app_crop = QtWidgets.QApplication(sys.argv)

    # Main instance of NadeOCR
    app = MainApp()
    app.run()

if __name__ == '__main__':
    run()