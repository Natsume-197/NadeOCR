from pynput import keyboard
from PySide6 import QtWidgets
from PySide6.QtGui import QIcon, Qt
from pynput.keyboard import Controller, Key
from PySide6.QtCore import QThread, QObject, Signal
from nadeocr.GUI.functions.utils.extra import edit_config_ini
from PySide6.QtWidgets import QWidget, QLabel, QPushButton


class InputHotkeyWidget(QWidget):
    shortcutChangedSignal = Signal()
    closeWindowSignal = Signal()

    def __init__(self, parent):
        self.parent = parent
        super(InputHotkeyWidget, self).__init__()

        self.ctrl_pressed = None
        self.alt_pressed = None
        self.shift_pressed = None
        self.key_pressed = None
        self.full_shortcut = ""
        self.registering_chord = False

        self.initUi()

        # Setup slots/signals
        self.shortcutChangedSignal.connect(self.update_current_shortcut)
        self.closeWindowSignal.connect(self.cancel_button)

        # Start components
        self.keyboard_listener = keyboard.Listener(
            on_press=self.for_canonical(self.on_press),
            on_release=self.for_canonical(self.on_release),
        )

        self.keyboard_listener.start()

    def initUi(self):
        self.setWindowTitle("Atajo")
        self.setFixedSize(335, 100)
        self.setWindowIcon(QIcon("./resources/assets/icon.ico"))

        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        self.label_hotkey = QLabel("Presione una serie de teclas para asignar un atajo")
        layout.addWidget(self.label_hotkey, 0, 0, 1, 5)

        self.label_hotkey_current = QLabel("...")
        self.label_hotkey_current.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_hotkey_current, 1, 0, 3, 5)

        self.button_accept = QPushButton("Aceptar", self)
        self.button_accept.clicked.connect(self.accept_button)
        self.button_cancel = QPushButton("Cancelar", self)
        self.button_cancel.clicked.connect(self.cancel_button)

        layout.addWidget(self.button_accept, 5, 3, 1, 1)
        layout.addWidget(self.button_cancel, 5, 4, 1, 1)

        self.show()

    def on_press(self, key):
        if not self.registering_chord:
            self.registering_chord = True

            # Reset keys
            self.ctrl_pressed = None
            self.alt_pressed = None
            self.shift_pressed = None
            self.key_pressed = None

        try:
            self.key_pressed = key.char

        except AttributeError:  # This exception means a Special key was pressed (Ctrl, Alt, Shift...)
            if key == keyboard.Key.esc:
                self.closeWindowSignal.emit()
                return False  # Close the thread

            self.toggle_modifier_key(key, True)

        # Note: on_press is executed on a separate Thread, so we must use the slot/signal system to update the UI from the Qt thread.
        # Not doing so could raise exceptions.
        self.shortcutChangedSignal.emit()

    def on_release(self, key):
        # Finish registering a chord of keys when we press an alphanumeric key
        if hasattr(key, "char"):
            self.registering_chord = False

        if self.registering_chord:
            self.toggle_modifier_key(key, False)

        # Note: on_release is executed on a separate Thread, so we must use the slot/signal system to update the UI from the Qt thread.
        # Not doing so could raise exceptions.
        self.shortcutChangedSignal.emit()

    def toggle_modifier_key(self, key, toggle):
        if (
            (key == keyboard.Key.ctrl)
            or (key == keyboard.Key.ctrl_l)
            or (key == keyboard.Key.ctrl_r)
        ):
            self.ctrl_pressed = f"<{key.name}>" if toggle else None
        if (
            (key == keyboard.Key.alt)
            or (key == keyboard.Key.alt_l)
            or (key == keyboard.Key.alt_r)
        ):
            self.alt_pressed = f"<{key.name}>" if toggle else None
        if (
            (key == keyboard.Key.shift)
            or (key == keyboard.Key.shift_l)
            or (key == keyboard.Key.alt_r)
        ):
            self.shift_pressed = f"<{key.name}>" if toggle else None

    def update_current_shortcut(self):
        self.full_shortcut = "+".join(
            filter(
                None,
                [
                    self.ctrl_pressed,
                    self.alt_pressed,
                    self.shift_pressed,
                    self.key_pressed,
                ],
            )
        )

        if self.full_shortcut:
            self.label_hotkey_current.setText(self.full_shortcut)
        else:
            self.label_hotkey_current.setText("...")

    def accept_button(self):
        print(f"Shortcut saved: {self.full_shortcut}")

        if self.full_shortcut:
            edit_config_ini("user_settings", "shortcut_key", self.full_shortcut)

            self.parent.shortcut_config()
            self.parent.button_input_hotkey.setText(self.full_shortcut)

        self.destroy_components()
        self.close()

    def cancel_button(self):
        self.destroy_components()
        self.close()

    def destroy_components(self):
        self.keyboard_listener.stop()

    def for_canonical(self, f):
        return lambda key: f(self.canonical_filter(key))

    def canonical_filter(self, key):
        # Pass Esc key as it is, so we can detect it later on the `on_press` method
        if key == keyboard.Key.esc:
            return key

        # canonical() removes any modifiers and returns the actual key pressed.
        # Examples:
        #  * Shift+a returns lowercase a, instead of uppercase A
        #  * Ctrl+<alphanumeric key> on japanese keyboards return the pressed key, instead of a composite character.
        return self.keyboard_listener.canonical(key)


class MainHotkeyExecution(QObject):
    def __init__(self, parent):
        self.parent = parent
        super(MainHotkeyExecution, self).__init__()
        self.input_widget = InputHotkeyWidget(parent=self.parent)
