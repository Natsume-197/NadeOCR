import io
from time import sleep
import pyperclip as pc
from google.cloud import vision
from google.oauth2 import service_account
from GUI.functions.utils.extra import read_config_ini, to_boolean

class GoogleProvider():
    def scan_google():
        config_reader = read_config_ini()
        
        is_split_line = to_boolean(config_reader["user_settings"]["copy_by_line"])
        remove_new_line = to_boolean(config_reader["user_settings"]["remove_new_line"])
        google_credentials = config_reader["path_settings"]["credentials_google"]
        
        creds = service_account.Credentials.from_service_account_file(google_credentials)

        path = './resources/temp/capture.png'
        client = vision.ImageAnnotatorClient(credentials=creds)
        
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
            
            if(is_split_line == True):
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