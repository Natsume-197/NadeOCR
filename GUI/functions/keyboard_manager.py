import keyboard
from PySide6.QtCore import Signal, QObject

shortcut_key = 'Alt+X'

# Listener for keyboard events using PySide6 and Signal
class KeyBoardManager(QObject):
    F1Signal = Signal()
    def start(self):
        keyboard.add_hotkey(shortcut_key, self.F1Signal.emit, suppress=True)
        