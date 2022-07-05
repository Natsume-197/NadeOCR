from GUI.functions.utils.extra import read_config_ini, edit_config_ini
import easyocr
import cv2 
import numpy as np

reader = easyocr.Reader(['ja', 'en'], gpu=True)

class EasyOCRProvider():
    def scan_easyocr():
        path = './resources/temp/capture.png'
        result = reader.readtext(path, detail = 0,  paragraph=True)
        print(result)
       

