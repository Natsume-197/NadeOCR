import platform
import sys
from GUI.tray_widget import SystemTray
from PySide6.QtWidgets import QApplication 
from GUI.options_widget import OptionsWidget

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
        # self.test = OptionsWidget(self)
        
    # Keeps the main process running until exit
    def run(self):
        sys.exit(self._app.exec())
        
    def __os_specific_setup(self):
        if platform.system() == "Windows":
            import ctypes
            # Assigning AppUserModelID in order to fix taskbar's icons for Windows
            id_app = 'natsume.nadeocr.0.3.0' 
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(id_app)

if __name__ == '__main__':
    app = MainApp()
    app.run()
