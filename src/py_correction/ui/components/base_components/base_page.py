from PySide6.QtWidgets import QWidget


class BasePage(QWidget):

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs) # type: ignore[arg-type]

        original_init = cls.__init__

        def wrapped_init(self, *args, **kwargs): # noqa
            self._is_page_initialized = False

            original_init(self, *args, **kwargs) # type: ignore[arg-type]

            if not self._is_page_initialized:
                raise RuntimeError(f"Page '{cls.__name__}' was instantiated without calling "
                                   f"self._init_ui() inside its __init__!")

        cls.__init__ = wrapped_init

    def _init_ui(self) -> None:
        self._is_page_initialized = True

        self._create_widgets()
        self._initialize_controllers()
        self._assemble_layout()

    def _create_widgets(self) -> None:
        ...

    def _initialize_controllers(self) -> None:
        ...

    def _assemble_layout(self) -> None:
        ...
