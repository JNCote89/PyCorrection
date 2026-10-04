import faulthandler
import traceback
""" Enable it in Windows PowerShell with $env:PYTHONFAULTHANDLER="1" and set to "force" the windows console mode flag """
faulthandler.enable()

from src.py_correction.sys_platform.linux_configurations import init_linux_qt_env

init_linux_qt_env()

import sys

def custom_excepthook(exc_type, exc_value, exc_traceback):
    """To debug Nuitka inside Windows"""
    print("--- Custom Except Handler ---")
    traceback.print_exception(exc_type, exc_value, exc_traceback)

sys.excepthook = custom_excepthook

from src.py_correction.ui.app import PyCorrectionApp


def main():
    app = PyCorrectionApp(sys.argv)
    sys.exit(app.run())


if __name__ == "__main__":
    main()