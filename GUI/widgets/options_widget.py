from PySide6 import QtWidgets
from PySide6.QtGui import QFont, QIcon
from GUI.widgets.input_hotkey_widget import MainHotkeyExecution
from GUI.functions.utils.extra import read_config_ini, edit_config_ini
from PySide6.QtWidgets import QFileDialog, QLineEdit, QSizePolicy, QSpacerItem, QWidget, QTabWidget, QLabel, QComboBox, QFrame, QCheckBox, QRadioButton, QPushButton, QTextEdit

class OptionsWidget(QWidget):
    def __init__(self, parent):
        self.parent = parent 
        super(OptionsWidget, self).__init__()
        self.setWindowTitle("Opciones")
        self.setFixedSize(425, 310)
        self.setWindowIcon(QIcon("./resources/assets/icon.ico"))

        self.config_reader = read_config_ini()
        
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)
        
        self.tabs = QTabWidget()
        self.tab_general = QWidget()
        self.tab_advanced = QWidget()
        self.tab_about = QWidget()
        
        self.tabs.addTab(self.tab_general,"General")
        self.tabs.addTab(self.tab_advanced,"Avanzado")
        self.tabs.addTab(self.tab_about,"Acerca de")
        
        # Create first tab layout
        self.tab_general.layout = QtWidgets.QGridLayout(self)
        self.tab_advanced.layout = QtWidgets.QGridLayout(self)
        self.tab_about.layout = QtWidgets.QGridLayout(self)

        # Add tabs to main widget
        layout.addWidget(self.tabs)
        self.tab_general.setLayout(self.tab_general.layout)
        self.tab_advanced.setLayout(self.tab_advanced.layout)
        self.tab_about.setLayout(self.tab_about.layout)

        # General Tab
        self.label_interface_user = QLabel("Interfaz de usuario")
        self.label_interface_user.setFont(QFont("Arial", 9, weight=QFont.Bold))
        self.tab_general.layout.addWidget(self.label_interface_user, 0, 0, 1, 5)
        
        self.label_language = QLabel("Idioma")
        self.tab_general.layout.addWidget(self.label_language, 1, 0)

        self.box_language = QComboBox()
        self.box_language.addItem("Español")
        self.box_language.addItem("Inglés")
        self.tab_general.layout.addWidget(self.box_language, 1, 1, 1, 5)
        
        self.label_notification_pos = QLabel("Posición notificación")
        self.tab_general.layout.addWidget(self.label_notification_pos, 2, 0, 1, 2)
        
        spanish_to_pos_text = {
            "TopLeft" : "Esquina superior izquierda",
            "TopRight" : "Esquina superior derecha", 
            "BottomLeft" : "Esquina inferior izquierda",
            "BottomRight" : "Esquina inferior derecha"
        }
        
        notification_pos = self.config_reader["user_settings"]["notification_pos"]
        self.box_notification_pos = QComboBox()
        self.box_notification_pos.addItem("Esquina superior izquierda")
        self.box_notification_pos.addItem("Esquina superior derecha")
        self.box_notification_pos.addItem("Esquina inferior izquierda")
        self.box_notification_pos.addItem("Esquina inferior derecha")
        self.box_notification_pos.setCurrentText(spanish_to_pos_text[notification_pos])
        self.tab_general.layout.addWidget(self.box_notification_pos, 2, 1, 1, 5)
                
        self.separatorLine = QFrame(frameShape=QFrame.HLine)   
        self.separatorLine.setLineWidth(0)
        self.separatorLine.setMidLineWidth(5)
        self.separatorLine.setStyleSheet("font: 9pt; color: grey;")
        self.tab_general.layout.addWidget(self.separatorLine, 4, 0, 1, 6)

        self.label_preferences_user = QLabel("Preferencias")
        self.label_preferences_user.setFont(QFont("Arial", 9, weight=QFont.Bold))
        self.tab_general.layout.addWidget(self.label_preferences_user, 5, 0)
        
        self.checkbox_run_startup = QCheckBox("Ejecutar al arranque", self)
        self.tab_general.layout.addWidget(self.checkbox_run_startup, 6, 0, 1, 2) 
        
        hotkey = self.config_reader["user_settings"]["shortcut_key"]

        self.label_preference_hotkey = QLabel("Atajo para escaneo")
        self.tab_general.layout.addWidget(self.label_preference_hotkey, 7, 0, 1, 2)
        self.parent.button_input_hotkey = QPushButton(self)
        self.parent.button_input_hotkey.setText(hotkey)
        self.tab_general.layout.addWidget(self.parent.button_input_hotkey, 7, 1, 1 , 5)    
        self.parent.button_input_hotkey.clicked.connect(self.on_button_hotkey_click)
        
        self.label_preference_scan = QLabel("Motor de escaneo preferido" )
        self.tab_general.layout.addWidget(self.label_preference_scan, 8, 0, 1, 3)
        
        self.radio_button_google = QRadioButton("Google (recomendado)")
        self.tab_general.layout.addWidget(self.radio_button_google, 9, 0)

        self.label_separator = QLabel("           ")
        self.tab_general.layout.addWidget(self.label_separator, 9, 1)
        self.radio_button_mangaocr = QRadioButton("MangaOCR")
        self.tab_general.layout.addWidget(self.radio_button_mangaocr, 9, 2)
        self.radio_button_paddleocr = QRadioButton("PaddleOCR")
        self.tab_general.layout.addWidget(self.radio_button_paddleocr, 9, 3)
        self.radio_button_paddleocr.setDisabled(True)         
        
        ocr_provider = self.config_reader["provider_settings"]["ocr_provider"]
        
        # OCR client selection based on the config file
        if(ocr_provider == "Google"):
            self.radio_button_google.setChecked(True)
            
        elif(ocr_provider == "MangaOCR"):
            self.radio_button_mangaocr.setChecked(True)

        self.spaceItem = QSpacerItem(100, 10, QSizePolicy.Expanding)
        self.tab_general.layout.addItem(self.spaceItem, 10, 0)  

        self.button_accept = QPushButton("Aceptar", self)
        self.button_cancel = QPushButton("Cancelar", self)
        self.button_accept.clicked.connect(self.accept_button)
        self.button_cancel.clicked.connect(self.cancel_button)

        self.tab_general.layout.addWidget(self.button_accept, 16,2, 2, 1)
        self.tab_general.layout.addWidget(self.button_cancel, 16,3, 2, 2)

        # Tab Advanced
        self.label_paths_user = QLabel("Rutas de archivos")
        self.label_paths_user.setFont(QFont("Arial", 9, weight=QFont.Bold))
        self.tab_advanced.layout.addWidget(self.label_paths_user, 0, 0, 1, 4)
    
        self.label_path_google = QLabel("Credenciales Google" )
        self.tab_advanced.layout.addWidget(self.label_path_google, 1, 0, 1, 2)
        
        self.line_edit_google = QLineEdit(self)
        self.tab_advanced.layout.addWidget(self.line_edit_google, 2, 0, 1, 5)
        
        self.button_accept_google = QPushButton("...", self)
        self.tab_advanced.layout.addWidget(self.button_accept_google, 2, 5, 1, 1)
        self.button_accept_google.clicked.connect(self.accept_button_path_google)

        path_string_google = self.config_reader["path_settings"]["credentials_google"]
        if(path_string_google.strip() == ''):
            self.line_edit_google.setText("No se ha definido")
        else:
            self.line_edit_google.setText(path_string_google)

        self.button_accept2 = QPushButton("Aceptar", self)
        self.button_cancel2 = QPushButton("Cancelar", self)
        self.button_accept2.clicked.connect(self.accept_button)
        self.button_cancel2.clicked.connect(self.cancel_button)

        self.tab_advanced.layout.addWidget(self.button_accept2, 16, 4, 2, 1)
        self.tab_advanced.layout.addWidget(self.button_cancel2, 16, 5, 2, 1)
        

        self.labelAbout = QLabel("<b>NadeOCR v1.0.0</b> (20/08/2022)<br>An easy and fast-to-use tool for scanning text anywhere with Google's Vision API and other third party services.<br><br>"
            "This project wouldn't be possible without:<br>- Google's Vision API for detecting and recognising a wide variety of languages including, but not limited to, English, Japanese and Spanish.<br>- The awesome Manga-OCR model by Maciej Budyś for recognizing Japanese characters in manga. <br><br>"
            "More information about this project can be found <a href='https://github.com/Natsume-197/NadeOCR'>here</a>.")
        self.labelAbout.setWordWrap(True)
        self.labelAbout.setOpenExternalLinks(True)
        self.tab_about.layout.addWidget(self.labelAbout, 0, 0, 1, 6)

        self.button_accept3 = QPushButton("Cerrar", self)
        self.button_accept3.clicked.connect(self.cancel_button)
        self.tab_about.layout.addWidget(self.button_accept3, 16, 5, 2, 1)

        self.tab_general.layout.setRowStretch(16, 5)  
        self.tab_advanced.layout.setRowStretch(15, 5)  
        self.tab_about.layout.setRowStretch(15, 5)  

        self.show()
        
    def accept_button_path_google(self):
        path_google_fdialog = QFileDialog.getOpenFileName(self, "Abrir archivo", "", "Credenciales (*.json)",  "")
        self.line_edit_google.setText(path_google_fdialog[0])
        edit_config_ini("path_settings", "credentials_google", path_google_fdialog[0])
        
    def accept_button(self):
        if self.radio_button_google.isChecked():
            edit_config_ini("provider_settings", "ocr_provider", "Google")
        elif(self.radio_button_mangaocr.isChecked()):
            edit_config_ini("provider_settings", "ocr_provider", "MangaOCR")
            
        if(self.box_notification_pos.currentText() == "Esquina superior izquierda"):
            edit_config_ini("user_settings", "notification_pos", "TopLeft")
        elif(self.box_notification_pos.currentText() == "Esquina superior derecha"):
            edit_config_ini("user_settings", "notification_pos", "TopRight")
        elif(self.box_notification_pos.currentText() == "Esquina inferior derecha"):
            edit_config_ini("user_settings", "notification_pos", "BottomRight")
        elif(self.box_notification_pos.currentText() == "Esquina inferior izquierda"):
            edit_config_ini("user_settings", "notification_pos", "BottomLeft")
                
        self.close()

    def cancel_button(self):
        self.close()
         
    def on_button_hotkey_click(self):
        self.input_hotkey_window = MainHotkeyExecution(parent=self.parent)
        
