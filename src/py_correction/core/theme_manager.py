from enum import StrEnum
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Slot
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QApplication
from matplotlib import font_manager, rcParams
import qdarktheme

from src.py_correction.core import nuitka_helpers
from src.py_correction.core.paths import FONT_DIRECTORY, THEME_DIRECTORY

if TYPE_CHECKING:
    from src.py_correction.core.event_bus import EventBus

logger = logging.getLogger(__name__)


class ThemeOptions(StrEnum):
    # Theme values for the QDarkTheme library
    DARK = "dark"
    LIGHT = "light"
    SYSTEM = "auto"


class ThemeManager(QObject):
    APP_QSS_FILE: Path = THEME_DIRECTORY.joinpath("theme.qss")
    APP_FONT_DIR: Path = FONT_DIRECTORY
    THEME_OPTIONS = ThemeOptions

    def __init__(self, event_bus: "EventBus"):
        super().__init__()
        self._event_bus = event_bus

        self._connect_downstream_signals()

    def _connect_downstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._event_bus.settings.uiThemeChanged,
                                    slot=self.set_ui_theme)

    def load_fonts(self) -> None:
        if not self.APP_FONT_DIR.exists():
            logger.warning(f"Font directory does not exist: {self.APP_FONT_DIR}")
            return

        for font_extension in ("*.ttf", "*.otf"):
            for font in self.APP_FONT_DIR.glob(font_extension):
                font_id = QFontDatabase.addApplicationFont(str(font.resolve()))
                if font_id == -1:
                    logger.warning(f"Font {font} not found")

                # Resolve a bug when initializing the font manager in the ui module.
                font_manager.fontManager.addfont(str(font.resolve()))
                rcParams['font.family'] = "Inter"

    @Slot(ThemeOptions)
    def set_ui_theme(self, selected_theme: ThemeOptions) -> None:
        app = QApplication.instance()
        if not app:
            return
        try:
            base_css = qdarktheme.load_stylesheet(selected_theme)
        except Exception as e:
            logger.warning(f"Failed to load qdarktheme {selected_theme}: {e}")
            base_css = ""

        custom_css = ""
        if self.APP_QSS_FILE.exists():
            try:
                custom_css = self.APP_QSS_FILE.read_text(encoding="utf-8")
            except IOError as e:
                logger.warning(f"Failed to load QSS file {self.APP_QSS_FILE}: {e}")
        else:
            logger.warning(f"QSS file does not exist: {self.APP_QSS_FILE}")

        combined_css = base_css + custom_css
        app.setStyleSheet(combined_css)  # type: ignore[arg-type]
