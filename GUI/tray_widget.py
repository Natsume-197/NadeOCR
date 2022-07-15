import sys
from GUI.crop_widget import CropWidget
from GUI.options_widget import OptionsWidget
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from GUI.functions.keyboard_manager import KeyBoardManager
from PySide6.QtGui import QIcon, QAction, QKeySequence
from GUI.functions.utils.extra import read_config_ini, to_boolean, edit_config_ini

icon_path = "./resources/assets/icon.ico"
keyboard_manager = KeyBoardManager()

class SystemTray(QSystemTrayIcon):
    def __init__(self, parent=None):
        QSystemTrayIcon.__init__(self)
        self.setIcon(QIcon(icon_path))
        menu = QMenu(parent)
         
        # Available actions in the Menu 
        self._scan_action = menu.addAction("Escanear", self.on_scan_click)
        
        menu.addSeparator()
        
        change_mode_menu = menu.addMenu("Cambiar modo")
        normal_mode_action = QAction("Normal", self, checkable=True)
        hiragana_mode_action = QAction("Hiragana", self, checkable=True)
        katakana_mode_action = QAction("Katakana", self, checkable=True)
        normal_mode_action.setChecked(True)

        change_mode_menu.addAction(normal_mode_action)
        change_mode_menu.addAction(hiragana_mode_action)
        change_mode_menu.addAction(katakana_mode_action)
         
        menu.addSeparator()
        
        config_reader = read_config_ini()
         
        self.split_copy_action = menu.addAction("Copiar línea por línea", None)
        self.split_copy_action.setChecked(to_boolean(config_reader["user_settings"]["copy_by_line"]))
        self.split_copy_action.setCheckable(True)
        self.split_copy_action.triggered.connect(self.on_split_click)
        
        self.split_remove_nl_action = menu.addAction("Remover salto de línea", None)
        self.split_remove_nl_action.setChecked(to_boolean(config_reader["user_settings"]["remove_new_line"]))
        self.split_remove_nl_action.setCheckable(True)
        self.split_remove_nl_action.triggered.connect(self.on_remove_new_line_click)

        menu.addSeparator()
        
        # self.history = menu.addAction("Historial")
        self.options = menu.addAction("Opciones", self.on_options_click)
        
        menu.addSeparator()
        
        self._exit_action = menu.addAction("Salir", self.on_exit_click)

        self.setContextMenu(menu)
         
        # Extra configuration
        self.setToolTip('NadeOCR')
        self.activated.connect(self.on_icon_click)
        
        self.shortcut_config()
        
        self.show()
                
    def shortcut_config(self):
        config_reader = read_config_ini()
        shortcut_key = config_reader["user_settings"]["shortcut_key"]
        keyboard_manager.F1Signal.connect(self.on_scan_click)
        self._scan_action.setShortcut(QKeySequence(shortcut_key))
        keyboard_manager.start()
        
    # Methods used for the actions available in the menu 
    def on_icon_click(self, reason):
        if reason == self.DoubleClick:
            self.on_scan_click()   
            
    def on_scan_click(self):
        self.window_crop = CropWidget()
            
    def on_exit_click(self):
        sys.exit()
        
    def on_split_click(self):
        edit_config_ini("user_settings", "copy_by_line", str(self.split_copy_action.isChecked()))
        
    def on_remove_new_line_click(self):
        edit_config_ini("user_settings", "remove_new_line", str(self.split_remove_nl_action.isChecked()))
          
    def on_options_click(self):
        self.window_options = OptionsWidget(parent=self)