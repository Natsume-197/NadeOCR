import io
# import pykakasi
from time import sleep
import pyperclip as pc
from google.cloud import vision
from GUI.widgets.toast_widget import QToaster
from GUI.widgets.popup_widget import PopupWidget
from google.oauth2 import service_account
from GUI.functions.utils.extra import read_config_ini, to_boolean, edit_config_ini

# kks = pykakasi.kakasi()

class GoogleProvider():

    def set_credentials():
        try:
            config_reader = read_config_ini()
            google_credentials = config_reader["path_settings"]["credentials_google"]
            google_credentials = service_account.Credentials.from_service_account_file(google_credentials)
        except FileNotFoundError:
            edit_config_ini("path_settings", "credentials_google", "")
            popup = PopupWidget()
            popup.show_info_messagebox("error", "Archivo de credenciales Google no encontrado. Actualice la ruta desde opciones.")
            
        except Exception as e:
            popup = PopupWidget()
            popup.show_info_messagebox("error", "Archivo de credenciales Google no válido. Verifique el archivo.")
            
        return google_credentials
        
    def scan_google(self):
        self.window_toast = QToaster()
        
        config_reader = read_config_ini()
        is_split_line = to_boolean(config_reader["user_settings"]["copy_by_line"])
        remove_new_line = to_boolean(config_reader["user_settings"]["remove_new_line"])        
        notification_pos = config_reader["user_settings"]["notification_pos"]
        path = './resources/temp/capture.png'
        
        google_credentials = GoogleProvider.set_credentials()
                
        client = vision.ImageAnnotatorClient(credentials=google_credentials)
        
        with io.open(path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        response = client.text_detection(image=image)
        texts = response.text_annotations
        sentences = []
    
        try:
            if (remove_new_line == True):
                result = texts[0].description.replace("\n", " ")
            else:
                result = texts[0].description
                # result = kks.convert(texts[0].description)
                # print(result[0])
                # result = result[0].get('hira')
            if(is_split_line == True):
                sentences = texts[0].description.splitlines()
                for i in range(len(sentences)):
                    sleep(0.3)
                    pc.copy(sentences[i])
                    print(sentences[i])
                    self.window_toast.showToaster(notification_pos, "Copiado exitoso.")
            else:
                pc.copy(result)
                self.window_toast.showToaster(notification_pos, "Copiado exitoso.")
                print(result)
                        
        except Exception as error:
            self.window_toast.showToaster(notification_pos, "No se encontro texto a escanear.")
            print(error)
        