import pyperclip as pc
from manga_ocr import MangaOcr
from GUI.toast_widget import QToaster

path = './resources/temp/capture.png'

mocr = MangaOcr()

class MangaOcrProvider():
    def scan_mangaocr(self):   
        self.window_toast = QToaster()
        try:
            text = mocr(path)
            print(text)
            pc.copy(text)
            self.window_toast.showToaster(1, "Copiado exitoso.")
        except Exception as e:
            print(e)
            self.window_toast.showToaster(1, "Error.")