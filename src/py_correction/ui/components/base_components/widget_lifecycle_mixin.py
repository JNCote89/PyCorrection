class WidgetLifecycleMixin:

    # Guard to make sure that partial components does not accidentally call self._init_ui() and connect multiple signals.
    _is_final_component: bool = False

    def __init__(self, *args, **kwargs) -> None:
        self._is_ui_initialized = False

    def _init_ui(self):
        if self._is_ui_initialized:
            raise RuntimeError(f"UI for {type(self).__name__} has already been initialized!")

        if not self._is_final_component:
            raise RuntimeError(f"Invalid Lifecycle Call: {type(self).__name__} is marked as a partial component "
                               "and cannot trigger _init_ui(). Only final widgets can execute the full lifecycle.")

        self._create_widgets()
        self._assemble_layout()
        self._connect_internal_signals()
        self._connect_downstream_signals()

        self._is_ui_initialized = True

    def _create_widgets(self) -> None:
        ...

    def _assemble_layout(self) -> None:
        ...

    def _connect_internal_signals(self) -> None:
        ...

    def _connect_downstream_signals(self) -> None:
        """ Connect the signal from the UI to the database
        [Page UI -> Page controller -> Service/Orchestrators -> Database] """
        ...
