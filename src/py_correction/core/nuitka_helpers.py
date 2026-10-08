from functools import wraps
import logging
from typing import Callable

from PySide6.QtCore import Signal, SignalInstance

logger = logging.getLogger(__name__)

def safe_connect(signal: "SignalInstance", slot: Callable | SignalInstance | Signal, overload: type | None = None):
    """
    Safely connects a Qt signal to a slot to prevent Nuitka compilation crashes with a direct connection.
    The event bus and the controllers were the main culprit of crashes throughout the codebase.
    Error messages such as "Segmentation fault" and "../PySide6-postLoad.py, line XX,
    in patched_connect SystemError: method_descriptor() returned a result with an exception set" are symptoms of
    failed connections.
    """
    if isinstance(slot, (SignalInstance, Signal)):
        return signal.connect(slot)

    if overload is not None:
        signal = signal[overload] # type: ignore[index]

    @wraps(slot)
    def _qt_safe_wrapper(*args):
        try:
            return slot(*args)
        except Exception as err:
            logger.critical(f"Exception encountered inside slot '{getattr(slot, '__name__', repr(slot))}' "
                            f"triggered by signal '{signal}': {err}", exc_info=True)
            raise

    return signal.connect(_qt_safe_wrapper)
