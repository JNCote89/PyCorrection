from PySide6.QtCore import QSignalBlocker, Slot
from PySide6.QtWidgets import QComboBox, QWidget
from typing_extensions import Any, override

from src.py_correction.core.domains.shared.shared_dtos import ComboBoxPayload
from src.py_correction.ui.components.base_components.widget_lifecycle_mixin import WidgetLifecycleMixin
from src.py_correction.ui.components.default_widgets.delegates.item_delegates import DefaultWordWrapDelegate


class PartialComboBox(QComboBox, WidgetLifecycleMixin):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)

    @override
    def _create_widgets(self) -> None:
        delegate = DefaultWordWrapDelegate(parent=self)
        self.setItemDelegate(delegate)

    @Slot(ComboBoxPayload)
    def populate_combo_box(self, payload: ComboBoxPayload) -> None:
        with QSignalBlocker(self):
            self.clear()
            for item in payload.items:
                self.addItem(item.label, item.internal_value)

        self._match_current_data_selection_index(current_data_selection=payload.current_data_selection)
        self.setEnabled(payload.is_enabled)

    def _on_index_changed(self, _index: int) -> None:
        # Each combo box must emit its own signal. The connect signal cannot be implemented in this class, as it
        # binds the base class to the signal and emit twice the child class signal.
        raise NotImplementedError("The child class must override this method.")

    def _match_current_data_selection_index(self, current_data_selection: Any) -> None:
        matching_index = self.findData(current_data_selection)
        if matching_index > 0:
            self.setCurrentIndex(matching_index)
        else:
            # To force emitting a signal after the initialization.
            if self.currentIndex() == 0:
                self._on_index_changed(0)
            else:
                self.setCurrentIndex(0)

    @override
    def wheelEvent(self, event) -> None:
        # Prevent double scrolling with the page and the combo box.
        if self.hasFocus() and self.view().isVisible():
            super().wheelEvent(event)
        else:
            event.ignore()
