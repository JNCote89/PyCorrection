import os
import tempfile
import traceback
from typing import TYPE_CHECKING

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QMessageBox, QSplashScreen

from src.py_correction.core import dependency_injection
from src.py_correction.core import logger
from src.py_correction.core import paths
from src.py_correction.database import connection
from src.py_correction.ui.feedbacks.user_notifications import UINotificationManager
from src.py_correction.ui.main_window.main_window_page import MainWindow

if TYPE_CHECKING:
    from src.py_correction.core.dependency_injection import DependencyInjectionContainer
    from src.py_correction.core.settings_manager import SettingsManager
    from src.py_correction.core.theme_manager import ThemeManager


class PyCorrectionApp(QApplication):

    def __init__(self, sys_argv):
        super().__init__(sys_argv)
        self._dependency_injection_container: "DependencyInjectionContainer | None" = None
        self._main_window: "MainWindow | None" = None
        self._settings_manager: "SettingsManager | None" = None
        self._theme_manager: "ThemeManager | None" = None
        self._ui_manager: "UINotificationManager | None" = None

    @property
    def dependency_injection_container(self) -> "DependencyInjectionContainer":
        if self._dependency_injection_container is None:
            raise RuntimeError("DI container accessed before app initialization!")
        return self._dependency_injection_container

    @dependency_injection_container.setter
    def dependency_injection_container(self, dependency_injection_container: "DependencyInjectionContainer"):
        self._dependency_injection_container = dependency_injection_container

    @property
    def main_window(self) -> "MainWindow":
        if self._main_window is None:
            raise RuntimeError("Main window accessed before app initialization!")
        return self._main_window

    @main_window.setter
    def main_window(self, main_window: "MainWindow"):
        self._main_window = main_window

    @property
    def settings_manager(self) -> "SettingsManager":
        if self._settings_manager is None:
            raise RuntimeError("Settings manager accessed before app initialization!")
        return self._settings_manager

    @settings_manager.setter
    def settings_manager(self, settings_manager: "SettingsManager"):
        self._settings_manager = settings_manager

    @property
    def theme_manager(self) -> "ThemeManager":
        if self._theme_manager is None:
            raise RuntimeError("Theme manager accessed before app initialization!")
        return self._theme_manager

    @theme_manager.setter
    def theme_manager(self, theme_manager: "ThemeManager"):
        self._theme_manager = theme_manager

    @property
    def ui_manager(self) -> "UINotificationManager":
        if self._ui_manager is None:
            raise RuntimeError("UI manager accessed before app initialization!")
        return self._ui_manager

    @ui_manager.setter
    def ui_manager(self, ui_manager: "UINotificationManager"):
        self._ui_manager = ui_manager

    def run(self):
        self._dismiss_nuitka_splash()
        """Boots up the splash screen and schedules the asynchronous app load."""
        splash = QSplashScreen(self._create_splash_pixmap(), Qt.WindowStaysOnTopHint)  # type: ignore
        splash.showMessage("""
                           <p style='color: #ffffff';>
                               Chargement de l'application PyCorrection.<br>
                               Cela peut prendre quelques secondes...
                           </p>
                           """,
                           alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
                           color=QColor("#ffffff"))
        splash.show()
        self.processEvents()

        QTimer.singleShot(50, lambda: self._load_and_start(splash))

        return self.exec()

    @staticmethod
    def _create_splash_pixmap() -> QPixmap:
        pixmap = QPixmap(400, 250)
        pixmap.fill(QColor("#222222"))

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        logo_path = paths.LOGO.joinpath("logo.png")
        logo_pixmap = QPixmap(str(logo_path)).scaled(96, 96, Qt.AspectRatioMode.KeepAspectRatio,
                                                     Qt.TransformationMode.SmoothTransformation)

        logo_x = (pixmap.width() - logo_pixmap.width()) // 2
        painter.drawPixmap(logo_x, 30, logo_pixmap)

        painter.setPen(QColor("#FFFFFF"))
        font = QFont("Arial", 18, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(0, 135, pixmap.width(), 40, Qt.AlignmentFlag.AlignCenter, "PyCorrection")

        painter.end()
        return pixmap

    @staticmethod
    def _dismiss_nuitka_splash():
        if "NUITKA_ONEFILE_PARENT" in os.environ:
            splash_filename = os.path.join(tempfile.gettempdir(),
                                           "onefile_%d_splash_feedback.tmp" % int(os.environ["NUITKA_ONEFILE_PARENT"]))
            if os.path.exists(splash_filename):
                try:
                    os.unlink(splash_filename)
                except OSError:
                    pass

    def _load_and_start(self, splash: QSplashScreen):
        """ Start the app once the splash screen is displayed """
        try:
            self._dependency_injection_container = dependency_injection.container
            if self._dependency_injection_container is not None:

                self._setup_app()
                self.main_window = MainWindow()
                self.main_window.show()

            splash.finish(self.main_window)

        except Exception as e:
            traceback_string = traceback.format_exc()
            print(traceback_string)
            log_file_path = paths.LOGS_DIRECTORY.joinpath("crash_log.txt")
            log_file_path.write_text(traceback_string, encoding="utf-8")

            splash.close()

            QMessageBox.critical(None, "Une erreur est survenue lors du lancement de l'application",
                                 f"""<p>Log :\n\n{str(e)}</p> 
                                          <p> Le détail est disponible dans les répertoire des logs
                                          dans le fichier "crash_log.txt"</p> """)

            self.exit(1)

    def _setup_app(self) -> None:
        """ Load heavy resources and databases once the app started """
        if self._dependency_injection_container is not None:

            self.settings_manager = self._dependency_injection_container.settings_manager()
            self.theme_manager = self._dependency_injection_container.theme_manager()

            logger.setup_logging()
            connection.init_db()

            self.ui_manager = UINotificationManager(parent=self)

            self.theme_manager.load_fonts()
            self.theme_manager.set_ui_theme(self.settings_manager.restored_settings.ui_theme)
