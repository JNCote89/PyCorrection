from PySide6.QtWidgets import QWidget


class BaseController(QWidget):

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs) # type: ignore[arg-type]

        original_init = cls.__init__

        def wrapped_init(self, *args, **kwargs): # noqa
            self._is_controller_initialized = False

            original_init(self, *args, **kwargs) # type: ignore[arg-type]

            if not self._is_controller_initialized:
                raise RuntimeError(f"Controller '{cls.__name__}' was instantiated without calling "
                                   f"self._init_controller() inside its __init__!")

        cls.__init__ = wrapped_init

    def _init_controller(self) -> None:
        self._is_controller_initialized = True

        self._connect_internal_signals()
        self._connect_downstream_signals()
        self._connect_upstream_signals()

        self._refresh_view()

    def _connect_internal_signals(self) -> None:
        ...

    def _connect_downstream_signals(self) -> None:
        """ Connect the signal from the UI to the database
        [Page UI -> Page controller -> Service/Orchestrators -> Database] """
        ...

    def _connect_upstream_signals(self) -> None:
        """ Connect the signal from the database to the UI
        [Database -> Service/Orchestrators -> Page controller -> Page UI]"""
        ...

    def _refresh_view(self) -> None:
        ...
