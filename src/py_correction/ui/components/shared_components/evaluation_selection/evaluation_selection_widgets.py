from typing import override

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QWidget

from src.py_correction.core import nuitka_helpers
from src.py_correction.ui.components.partial_widgets.combo_boxes import PartialComboBox


class EvaluationIDComboBox(PartialComboBox):
    _is_final_component = True

    evaluationIDChanged = Signal(object)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._init_ui()

    @override
    def _connect_downstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self.currentIndexChanged,
                                    slot=self._on_index_changed)

    def synchronized_evaluation_id(self, evaluation_id: int | None):
        self.blockSignals(True)
        if evaluation_id is not None:
            matching_index = self.findData(evaluation_id)
            if matching_index >= 0:
                self.setCurrentIndex(matching_index)
        else:
            self.setCurrentIndex(0)
        self.blockSignals(False)

    @Slot(int)
    @override
    def _on_index_changed(self, _index: int) -> None:
        evaluation_selected = self.currentData()
        self.evaluationIDChanged.emit(evaluation_selected)


