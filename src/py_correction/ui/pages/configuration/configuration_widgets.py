from typing import override

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QWidget

from src.py_correction.core import nuitka_helpers
from src.py_correction.core.domains.shared.shared_enums import AutofillOptions
from src.py_correction.core.settings_manager import ThemeOptions
from src.py_correction.engine.reference.csl.csl_enum import CitationStyle
from src.py_correction.ui.components.partial_widgets.combo_boxes import PartialComboBox


class ThemeComboBox(PartialComboBox):
    _is_final_component = True

    uiThemeChanged = Signal(ThemeOptions)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._init_ui()

    @override
    def _connect_internal_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self.currentIndexChanged,
                                    slot=self._on_index_changed)

    @Slot(int)
    @override
    def _on_index_changed(self, _index: int) -> None:
        selected_theme = ThemeOptions(self.currentData())
        self.uiThemeChanged.emit(selected_theme)


class EvaluationAutofillComboBox(PartialComboBox):
    _is_final_component = True

    evaluationAutofillChanged = Signal(AutofillOptions)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._init_ui()

    @override
    def _connect_internal_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self.currentIndexChanged,
                                    slot=self._on_index_changed)

    @Slot(int)
    @override
    def _on_index_changed(self, _index: int) -> None:
        autofill_option_selected = AutofillOptions(self.currentData())
        self.evaluationAutofillChanged.emit(autofill_option_selected)


class CitationStyleComboBox(PartialComboBox):
    """This widget is disabled inside the settings_mappers module because there is only one style available in the
    beta version. The widget will be enabled when more style will be added. """
    _is_final_component = True

    citationStyleChanged = Signal(CitationStyle)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._init_ui()

    @override
    def _connect_internal_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self.currentIndexChanged,
                                    slot=self._on_index_changed)

    @Slot(int)
    @override
    def _on_index_changed(self, _index: int) -> None:
        citation_style_selected = CitationStyle(self.currentData())
        self.citationStyleChanged.emit(citation_style_selected)
