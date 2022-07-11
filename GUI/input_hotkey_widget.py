from pynput import keyboard
from pynput.keyboard import KeyCode
from PySide6 import QtWidgets
from PySide6.QtGui import QIcon, Qt
from pynput.keyboard import Controller, Key
from PySide6.QtCore import QThread, QObject, Signal
from GUI.functions.utils.extra import edit_config_ini
from PySide6.QtWidgets import QWidget, QLabel, QPushButton
from GUI.functions.utils.constants import keycode_to_string

SHIFT_STATE = False
CONTROL_STATE = False
ALT_STATE = False
CURRENT_VALUE = ''
ARRAY = []

class ListenKeyboard(QThread):
            
    finished_signal = Signal(str)
    
    def __init__(self, parent=None):
         QThread.__init__(self, parent)
         
    def run(self):
        self.Listen()
        
    def on_press(self, key):
        global SHIFT_STATE
        global CONTROL_STATE
        global ALT_STATE
        
        if key == keyboard.Key.ctrl_l:
            CONTROL_STATE = True
        elif key == keyboard.Key.shift:
            SHIFT_STATE = True
        elif key == keyboard.Key.alt_l:
            ALT_STATE = True
        else:
            try:
                if CONTROL_STATE:
                    ARRAY.append("ctrl")
                if SHIFT_STATE:
                    ARRAY.append("shift")
                if ALT_STATE:
                    ARRAY.append("alt")
                else:
                    pass
                if key.char in keycode_to_string:
                    ARRAY.append(keycode_to_string[key.char])
                else:
                    key = '{0}'.format(key)
                    ARRAY.append(keycode_to_string[key])
                    # print('{0} pressed'.format(key))
                    print(ARRAY)
                textLabel = '+' .join(map(str, ARRAY))
                textLabel = textLabel.replace("'", "")
                self.finished_signal.emit(textLabel)
            except Exception as e:
                print(e)

    def on_release(self, key):
        global SHIFT_STATE
        global CONTROL_STATE
        global ALT_STATE
        # An interesting workarouund because I couldn't figure a way to close the looping thread properly from GUI
        if key == keyboard.Key.esc:
            # Stop listener
            return False
        if key == keyboard.Key.shift:
            SHIFT_STATE = False
        if key == keyboard.Key.ctrl_l:
            CONTROL_STATE = False
        if key == keyboard.Key.alt_l:
            ALT_STATE = False
        ARRAY.clear()
            
    def Listen(self):
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()
            
class InputHotkeyWidget(QWidget):
    
    listener_thread = ListenKeyboard()
    
    def __init__(self, parent):
        self.parent = parent
        super(InputHotkeyWidget, self).__init__()
                
        self.initUi()

        # Trigger listener
        self.label_hotkey_current.setText("...")
        self.listener_thread.finished_signal.connect(self.update_label_hotkey)

        self.listener_thread.start()
        
    def initUi(self):
        self.setWindowTitle("Atajo")
        self.setFixedSize(335, 100)
        self.setWindowIcon(QIcon("./resources/assets/icon.ico"))
        
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)
        
        self.label_hotkey = QLabel("Presione una serie de teclas para asignar un atajo")
        layout.addWidget(self.label_hotkey, 0, 0, 1, 5)

        self.label_hotkey_current = QLabel("------")
        self.label_hotkey_current.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_hotkey_current, 1, 0, 3, 5)

        self.button_accept = QPushButton("Aceptar", self)
        self.button_accept.clicked.connect(self.accept_button)
        self.button_cancel = QPushButton("Cancelar", self)
        self.button_cancel.clicked.connect(self.cancel_button)

        layout.addWidget(self.button_accept, 5,3, 1, 1)
        layout.addWidget(self.button_cancel, 5,4, 1, 1)
        
        self.show()
    
    def accept_button(self):
        edit_config_ini("user_settings", "shortcut_key", CURRENT_VALUE)

        keyboard = Controller()
        keyboard.press(Key.esc)
        keyboard.release(Key.esc)

        self.parent.shortcut_config()
        self.parent.button_input_hotkey.setText(CURRENT_VALUE)
                        
        self.close()
            
    def cancel_button(self):
        keyboard = Controller()
        keyboard.press(Key.esc)
        keyboard.release(Key.esc)
        
        self.close()
        
    def update_label_hotkey(self, textLabel):
        global CURRENT_VALUE
        self.label_hotkey_current.setText(textLabel)
        CURRENT_VALUE = textLabel
        
class MainHotkeyExecution(QObject):
    def __init__(self, parent):
        self.parent = parent
        super(MainHotkeyExecution, self).__init__()
        self.input_widget = InputHotkeyWidget(parent=self.parent)
