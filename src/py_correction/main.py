from src.py_correction.sys_platform.linux_configurations import init_linux_qt_env

init_linux_qt_env()

import sys

from src.py_correction.ui.app import PyCorrectionApp


def main():
    app = PyCorrectionApp(sys.argv)
    sys.exit(app.run())


if __name__ == "__main__":
    main()