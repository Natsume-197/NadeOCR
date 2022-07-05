from PySide6 import QtWidgets
from PySide6.QtGui import QFont, QIcon
from GUI.input_hotkey_widget import MainHotkeyExecution
from GUI.functions.utils.extra import read_config_ini, edit_config_ini
from PySide6.QtWidgets import QSizePolicy, QSpacerItem, QWidget, QTabWidget, QLabel, QComboBox, QFrame, QCheckBox, QRadioButton, QPushButton

class OptionsWidget(QWidget):
    def __init__(self, parent):
        self.parent = parent 
        super(OptionsWidget, self).__init__()
        self.setWindowTitle("Opciones")
        self.setFixedSize(400, 285)
        self.setWindowIcon(QIcon("./resources/assets/icon.ico"))

        # self.parent.print_x("invocado desde la clase options")
                
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
        
        # Add tabs to main widget
        layout.addWidget(self.tabs)
        self.tab_general.setLayout(self.tab_general.layout)
        
        # General Tab
        self.label_interface_user = QLabel("Interfaz de usuario")
        self.label_interface_user.setFont(QFont("Arial", 9, weight=QFont.Bold))
        self.tab_general.layout.addWidget(self.label_interface_user, 0, 0, 1, 4)
        
        self.label_language = QLabel("Idioma")
        self.tab_general.layout.addWidget(self.label_language, 1, 0)

        self.box_language = QComboBox()
        self.box_language.addItem("Español", "Inglés")
        self.box_language.addItem("Inglés")
        self.tab_general.layout.addWidget(self.box_language, 1, 1, 1, 3)
                
        self.separatorLine = QFrame(frameShape=QFrame.HLine)   
        self.separatorLine.setLineWidth(0)
        self.separatorLine.setMidLineWidth(5)
        self.separatorLine.setStyleSheet("font: 9pt; color: grey;")
        self.tab_general.layout.addWidget(self.separatorLine, 3, 0, 1, 4)

        self.label_preferences_user = QLabel("Preferencias")
        self.label_preferences_user.setFont(QFont("Arial", 9, weight=QFont.Bold))
        self.tab_general.layout.addWidget(self.label_preferences_user, 4, 0)
        
        self.checkbox_run_startup = QCheckBox("Ejecutar al arranque", self)
        self.tab_general.layout.addWidget(self.checkbox_run_startup, 5, 0, 1, 2) 
        
        config_reader = read_config_ini()
        
        hotkey = config_reader["user_settings"]["shortcut_key"]

        self.label_preference_hotkey = QLabel("Atajo para escaneo rápido")
        self.tab_general.layout.addWidget(self.label_preference_hotkey, 6, 0, 1, 2)
        self.parent.button_input_hotkey = QPushButton(self)
        self.parent.button_input_hotkey.setText(hotkey)
        self.tab_general.layout.addWidget(self.parent.button_input_hotkey, 6, 2, 1 , 2)    
        self.parent.button_input_hotkey.clicked.connect(self.on_button_hotkey_click)
        
        self.label_preference_scan = QLabel("Motor de escaneo preferido" )
        self.tab_general.layout.addWidget(self.label_preference_scan, 7, 0, 1, 3)
        
        self.radio_button_google = QRadioButton("Google")
        self.tab_general.layout.addWidget(self.radio_button_google, 8, 0)
        self.radio_button_mangaocr = QRadioButton("MangaOCR")
        self.tab_general.layout.addWidget(self.radio_button_mangaocr, 8, 1)
        self.radio_button_tesseract = QRadioButton("Tesseract")
        self.tab_general.layout.addWidget(self.radio_button_tesseract, 8, 2)
        self.radio_button_tesseract.setDisabled(True)       
        self.radio_button_easyocr = QRadioButton("EasyOCR")
        self.tab_general.layout.addWidget(self.radio_button_easyocr, 8, 3)   
        self.radio_button_easyocr.setDisabled(True)  
        
        ocr_provider = config_reader["provider_settings"]["ocr_provider"]
        
        # OCR client selection based on the config file
        if(ocr_provider == "Google"):
            self.radio_button_google.setChecked(True)
            
        elif(ocr_provider == "MangaOCR"):
            self.radio_button_mangaocr.setChecked(True)
            
        elif(ocr_provider == "Tesseract"):
            self.radio_button_tesseract.setChecked(True)
            
        elif(ocr_provider == "EasyOCR"):
            self.radio_button_easyocr.setChecked(True)

        self.spaceItem = QSpacerItem(100, 10, QSizePolicy.Expanding)
        self.tab_general.layout.addItem(self.spaceItem, 9, 0)  

        self.button_accept = QPushButton("Aceptar", self)
        self.button_cancel = QPushButton("Cancelar", self)
        self.button_accept.clicked.connect(self.accept_button)
        self.button_cancel.clicked.connect(self.cancel_button)

        self.tab_general.layout.addWidget(self.button_accept, 15,2)
        self.tab_general.layout.addWidget(self.button_cancel, 15,3)

        layout.setRowStretch(6, 2)  
        self.show()
        
    def accept_button(self):
        if self.radio_button_google.isChecked():
            edit_config_ini("provider_settings", "ocr_provider", "Google")
        elif(self.radio_button_tesseract.isChecked()):
            edit_config_ini("provider_settings", "ocr_provider", "Tesseract")
        elif(self.radio_button_easyocr.isChecked()):
            edit_config_ini("provider_settings", "ocr_provider", "EasyOCR")
        elif(self.radio_button_mangaocr.isChecked()):
            edit_config_ini("provider_settings", "ocr_provider", "MangaOCR")
                
        self.close()

    def cancel_button(self):
        self.close()
         
    def on_button_hotkey_click(self):
        self.input_hotkey_window = MainHotkeyExecution(parent=self.parent)
        
