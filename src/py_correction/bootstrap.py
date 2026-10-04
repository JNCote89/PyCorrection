"""
src/py_correction/bootstrap.py
Handles platform-specific runtime initialization, GUI console redirects,
and exception handling for standard Python execution and Nuitka standalone builds.
"""

import faulthandler
import os
import sys
import traceback

import matplotlib

from src.py_correction.sys_platform.linux_configurations import init_linux_qt_env


def setup_windows_console_redirect():
    """Redirect stdout and stderr to devnull when running in Windows --windows-disable-console mode."""
    if sys.stdout is None or sys.stderr is None:
        devnull = open(os.devnull, "w", encoding="utf-8")
        if sys.stdout is None:
            sys.stdout = devnull
        if sys.stderr is None:
            sys.stderr = devnull


def _custom_excepthook(exc_type, exc_value, exc_traceback):
    """Custom exception hook to log uncaught exceptions in compiled/windowed mode."""
    print("--- Uncaught Exception ---")
    traceback.print_exception(exc_type, exc_value, exc_traceback)


def setup_exception_handling():
    """Enable faulthandler and set custom exception hook for debugging."""
    # Enable faulthandler (can be enabled via $env:PYTHONFAULTHANDLER="1" in PowerShell)
    faulthandler.enable()
    sys.excepthook = _custom_excepthook


def initialize_environment():
    """Run all pre-Qt initialization tasks."""
    setup_windows_console_redirect()
    setup_exception_handling()
    init_linux_qt_env()

    # Configure backend before importing matplotlib.pyplot or creating Qt instances
    matplotlib.use("QtAgg")