from functools import wraps
from typing import Callable

from PySide6.QtCore import Signal, SignalInstance


def safe_connect(signal: "SignalInstance", slot: Callable):
    """
    Safely connects a Qt signal to a slot to prevent Nuitka compilation crashes with a direct connection.
    The event bus and the controllers were the main culprit of crashes throughout the codebase.
    Error messages such as "Segmentation fault" and "../PySide6-postLoad.py, line XX,
    in patched_connect SystemError: method_descriptor() returned a result with an exception set" are symptoms of
    failed connections.
    """
    if isinstance(slot, (SignalInstance, Signal)):
        return signal.connect(slot)

    @wraps(slot)
    def _qt_safe_wrapper(*args):
        return slot(*args)

    return signal.connect(_qt_safe_wrapper)