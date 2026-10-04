import sys

from src.py_correction.bootstrap import initialize_environment

# Initialize OS fixes, exception hooks, Matplotlib backend, and Qt environment settings
initialize_environment()

from src.py_correction.ui.app import PyCorrectionApp


def main():
    app = PyCorrectionApp(sys.argv)
    sys.exit(app.run())


if __name__ == "__main__":
    main()