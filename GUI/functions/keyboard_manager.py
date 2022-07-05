import keyboard
from PySide6.QtCore import Signal, QObject
from GUI.functions.utils.extra import read_config_ini, edit_config_ini

# Listener for keyboard events using PySide6 and Signal
class KeyBoardManager(QObject):
    F1Signal = Signal()
    def start(self):
        config_reader = read_config_ini()
        shortcut_key = config_reader["user_settings"]["shortcut_key"]
        keyboard.add_hotkey(shortcut_key, self.F1Signal.emit, suppress=True)
        