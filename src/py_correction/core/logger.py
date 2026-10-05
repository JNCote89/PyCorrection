import logging
from logging.handlers import RotatingFileHandler
import sys

from PySide6.QtCore import QObject, Signal

from src.py_correction.core.paths import LOGS_DIRECTORY

DEBUG_MODE = False
DEBUG_DB_MODE = False


class QtLogSignals(QObject):
    log_emitted = Signal(str, str)


qt_log_bridge = QtLogSignals()


class QtSignalingHandler(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        qt_log_bridge.log_emitted.emit(msg, record.levelname)


class InfoFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.INFO


class AppOnlyFilter(logging.Filter):
    def __init__(self, allowed_prefixes=("py_correction", "__main__")):
        super().__init__()
        self.allowed_prefixes = allowed_prefixes

    def filter(self, record):
        return any(record.name.startswith(prefix) for prefix in self.allowed_prefixes)


def setup_logging(app_module_name="src"):
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    root_logger.handlers.clear()

    qt_handler = QtSignalingHandler()

    formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s', datefmt='%H:%M:%S')

    qt_handler.setFormatter(formatter)
    qt_handler.setLevel(logging.INFO)
    qt_handler.addFilter(InfoFilter())

    debug_file_handler = RotatingFileHandler(LOGS_DIRECTORY / "debug.log",
                                             mode="a",
                                             maxBytes=2 * 1024 * 1024,
                                             backupCount=1,
                                             encoding="utf-8")
    debug_file_handler.setLevel(logging.DEBUG)
    debug_file_handler.setFormatter(formatter)


    info_file_handler = RotatingFileHandler(LOGS_DIRECTORY / "info.log",
                                            mode="a",
                                            maxBytes=2 * 1024 * 1024,
                                            backupCount=1,encoding="utf-8")
    info_file_handler.setLevel(logging.INFO)
    info_file_handler.setFormatter(formatter)
    info_file_handler.addFilter(InfoFilter())

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    if not DEBUG_MODE:
        app_filter = AppOnlyFilter(allowed_prefixes=(app_module_name, "__main__"))
        qt_handler.addFilter(app_filter)
        debug_file_handler.addFilter(app_filter)
        info_file_handler.addFilter(app_filter)
        console_handler.addFilter(app_filter)

    root_logger.addHandler(qt_handler)
    root_logger.addHandler(debug_file_handler)
    root_logger.addHandler(info_file_handler)
    root_logger.addHandler(console_handler)

    def _handle_crash(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        root_logger.critical("Application crashed unexpectedly!",exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = _handle_crash
