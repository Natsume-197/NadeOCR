import io
import os

# import pykakasi
from time import sleep

import pyperclip as pc
from google.cloud import vision
from google.oauth2 import service_account

from nadeocr.GUI.functions.utils.extra import (
    edit_config_ini,
    get_data,
    read_config_ini,
    to_boolean,
)
from nadeocr.GUI.widgets.popup_widget import PopupWidget
from nadeocr.GUI.widgets.toast_widget import QToaster

# kks = pykakasi.kakasi()
_ROOT = os.path.abspath(os.path.dirname(__file__))


class GoogleProvider:
    def __init__(self, parent):
        self.parent = parent
        super(GoogleProvider, self).__init__()

    def set_credentials():
        try:
            config_reader = read_config_ini()
            google_credentials = config_reader["path_settings"]["credentials_google"]
            google_credentials = service_account.Credentials.from_service_account_file(
                google_credentials
            )
        except FileNotFoundError:
            edit_config_ini("path_settings", "credentials_google", "")
            popup = PopupWidget()
            popup.show_info_messagebox(
                "error",
                "Archivo de credenciales Google no encontrado. Actualice la ruta desde opciones.",
            )

        except Exception as e:
            popup = PopupWidget()
            popup.show_info_messagebox(
                "error",
                "Archivo de credenciales Google no válido. Verifique el archivo.",
            )

        return google_credentials

    def scan_google(self):
        config_reader = read_config_ini()
        is_split_line = to_boolean(config_reader["user_settings"]["copy_by_line"])
        remove_new_line = to_boolean(config_reader["user_settings"]["remove_new_line"])
        notification_pos = config_reader["user_settings"]["notification_pos"]

        path = get_data(_ROOT, "./../../resources/temp", "capture.png")

        google_credentials = GoogleProvider.set_credentials()

        if google_credentials == "":
            return

        client = vision.ImageAnnotatorClient(credentials=google_credentials)

        with io.open(path, "rb") as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        response = client.text_detection(image=image)
        texts = response.text_annotations
        sentences = []

        try:
            if remove_new_line == True:
                result = texts[0].description.replace("\n", " ")
            else:
                result = texts[0].description
                # result = kks.convert(texts[0].description)
                # print(result[0])
                # result = result[0].get('hira')
            if is_split_line == True:
                sentences = texts[0].description.splitlines()
                for i in range(len(sentences)):
                    sleep(0.3)
                    pc.copy(sentences[i])
                    print(sentences[i])
                    self.parent.window_toast.showToaster(
                        notification_pos, "Copiado exitoso."
                    )
            else:
                pc.copy(result)
                self.parent.window_toast.showToaster(
                    notification_pos, "Copiado exitoso."
                )
                print(result)

        except Exception as error:
            self.parentwindow_toast.showToaster(
                notification_pos, "No se encontro texto a escanear."
            )
            print(error)
