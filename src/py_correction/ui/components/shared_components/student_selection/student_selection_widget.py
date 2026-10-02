from typing import override

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QWidget

from src.py_correction.ui.components.partial_widgets.combo_boxes import PartialComboBox


class StudentIDComboBox(PartialComboBox):
    _is_final_component = True

    studentIDChanged = Signal(object)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._init_ui()

    @override
    def _connect_downstream_signals(self) -> None:
        self.currentIndexChanged.connect(self._on_index_changed)

    def synchronized_student_id(self, student_id: int | None):
        self.blockSignals(True)
        if student_id is not None:
            matching_index = self.findData(student_id)
            if matching_index >= 0:
                self.setCurrentIndex(matching_index)
        else:
            self.setCurrentIndex(0)
        self.blockSignals(False)

    @Slot(int)
    @override
    def _on_index_changed(self, _index: int) -> None:
        student_selected = self.currentData()
        self.studentIDChanged.emit(student_selected)

