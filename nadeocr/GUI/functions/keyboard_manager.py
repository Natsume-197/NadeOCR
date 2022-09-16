from PySide6.QtCore import Signal, QObject
from nadeocr.GUI.functions.utils.extra import read_config_ini
from pynput import keyboard

# Listener for keyboard events using PySide6 and Signal
class KeyBoardManager(QObject):
    F1Signal = Signal()

    def start(self):
        config_reader = read_config_ini()
        shortcut_key = config_reader["user_settings"]["shortcut_key"]

        capture_hotkey = keyboard.HotKey(
            keyboard.HotKey.parse(shortcut_key), self.F1Signal.emit
        )

        # TODO: Ideally this should be defined on __init__ to avoid having to check if listener is defined.
        if hasattr(self, "listener"):
            print("Resetting keyboard listener thread")
            self.listener.stop()

        self.listener = keyboard.Listener(
            on_press=self.for_canonical(capture_hotkey.press),
            on_release=self.for_canonical(capture_hotkey.release),
        )

        self.listener.start()

    def for_canonical(self, f):
        # canonical() removes any modifiers and returns the actual key pressed.
        # Examples:
        #  * Shift+a returns lowercase a, instead of uppercase A
        #  * Ctrl+<alphanumeric key> on japanese keyboards return the pressed key, instead of a composed character.
        return lambda k: f(self.listener.canonical(k))
