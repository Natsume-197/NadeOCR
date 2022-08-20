import pyperclip as pc
from manga_ocr import MangaOcr
from GUI.widgets.toast_widget import QToaster
from GUI.functions.utils.extra import read_config_ini

# mocr = MangaOcr()
path = './resources/temp/capture.png'

class MangaOcrProvider():
    def scan_mangaocr(self):   
        self.window_toast = QToaster()
        config_reader = read_config_ini()
        notification_pos = config_reader["user_settings"]["notification_pos"]
        try:
            text = mocr(path)
            print(text)
            pc.copy(text)
            self.window_toast.showToaster(notification_pos, "Copiado exitoso")
        except Exception as e:
            print(e)
            self.window_toast.showToaster(notification_pos, "Error al copiar")