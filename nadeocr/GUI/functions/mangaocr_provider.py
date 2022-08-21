import os
import pyperclip as pc
from nadeocr.GUI.functions.utils.extra import read_config_ini, get_data

_ROOT = os.path.abspath(os.path.dirname(__file__))

path = get_data(_ROOT, "./../../resources/temp", "capture.png")

class MangaOcrProvider():
    def __init__(self, parent):
        self.parent = parent 
        super(MangaOcrProvider, self).__init__()

    def scan_mangaocr(self):   
        config_reader = read_config_ini()
        notification_pos = config_reader["user_settings"]["notification_pos"]
        try:
            text = self.parent.ocrModelManga(path)
            print(text)
            pc.copy(text)
            self.parent.window_toast.showToaster(notification_pos, "Copiado exitoso")
        except Exception as e:
            print(e)
            self.parent.window_toast.showToaster(notification_pos, "Error al copiar")