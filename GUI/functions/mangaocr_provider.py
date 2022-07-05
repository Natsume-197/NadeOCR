from manga_ocr import MangaOcr
import pyperclip as pc

path = './resources/temp/capture.png'

mocr = MangaOcr()

class MangaOcrProvider():
    def scan_mangaocr():   
        text = mocr(path)
        print(text)
        pc.copy(text)