import os
import sys

import requests
from manga_ocr import MangaOcr
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

from nadeocr.GUI.functions.keyboard_manager import KeyBoardManager
from nadeocr.GUI.functions.utils.extra import (
    edit_config_ini,
    get_data,
    read_config_ini,
    to_boolean,
)
from nadeocr.GUI.widgets.crop_widget import CropWidget
from nadeocr.GUI.widgets.options_widget import OptionsWidget
from nadeocr.GUI.widgets.toast_widget import QToaster

_ROOT = os.path.abspath(os.path.dirname(__file__))
keyboard_manager = KeyBoardManager()


class SystemTray(QSystemTrayIcon):
    def __init__(self, parent=None):
        QSystemTrayIcon.__init__(self)

        self.window_toast = QToaster()
        self.ocrModelManga = None
        icon_path = get_data(_ROOT, "../../resources/assets", "icon_loading.ico")

        """ 
        self.threadpool = QThreadPool()
        worker = BaseWorker(method)
        worker.signals.result.connect(secondMethon)
        self.threadpool.start(worker)
        """

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
        self.split_copy_action.setChecked(
            to_boolean(config_reader["user_settings"]["copy_by_line"])
        )
        self.split_copy_action.setCheckable(True)
        self.split_copy_action.triggered.connect(self.on_split_click)

        self.split_remove_nl_action = menu.addAction("Remover salto de línea", None)
        self.split_remove_nl_action.setChecked(
            to_boolean(config_reader["user_settings"]["remove_new_line"])
        )
        self.split_remove_nl_action.setCheckable(True)
        self.split_remove_nl_action.triggered.connect(self.on_remove_new_line_click)

        menu.addSeparator()

        # self.history = menu.addAction("Historial")
        self.options = menu.addAction("Opciones", self.on_options_click)

        menu.addSeparator()

        self._exit_action = menu.addAction("Salir", self.on_exit_click)

        self.setContextMenu(menu)

        # Extra configuration
        self.setToolTip("NadeOCR")
        self.activated.connect(self.on_icon_click)

        self.shortcut_config()

        self.show()
        self.showMessage("Información", "Por favor, espere. Cargando aplicación...")
        self.ocrModelManga = MangaOcr()
        icon_path = get_data(_ROOT, "../../resources/assets", "icon.ico")
        self.setIcon(QIcon(icon_path))
        self.showMessage("Información", "Aplicación lista para usarse.")

        # Check latest update for NadeOCR from Github
        current_version = config_reader["user_settings"]["current_version"]
        self.check_latest_update(current_version)

    def check_latest_update(self, current_version):
        try:
            response = requests.get(
                "https://api.github.com/repos/Natsume-197/NadeOCR/releases/latest"
            )
        except Exception as e:
            return

        self.latest = int(
            response.json()["name"].split("v", 1)[1].strip().replace(".", "")
        )
        self.current_version = int(current_version.strip().replace(".", ""))

        if self.latest > self.current_version:
            self.showMessage(
                "Información",
                "Hay una nueva actualización de NadeOCR disponible en Github.",
            )
        elif self.latest == current_version:
            pass

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
        self.window_crop = CropWidget(parent=self)

    def on_exit_click(self):
        sys.exit()

    def on_split_click(self):
        edit_config_ini(
            "user_settings", "copy_by_line", str(self.split_copy_action.isChecked())
        )

    def on_remove_new_line_click(self):
        edit_config_ini(
            "user_settings",
            "remove_new_line",
            str(self.split_remove_nl_action.isChecked()),
        )

    def on_options_click(self):
        self.window_options = OptionsWidget(parent=self)
