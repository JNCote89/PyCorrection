from enum import IntEnum
from typing import override

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPaintEvent, QPainter
from PySide6.QtWidgets import QListView, QListWidget, QListWidgetItem, QSizePolicy, QWidget

from src.py_correction.core.domains.shared.shared_dtos import WidgetItem
from src.py_correction.ui.components.base_components.widget_lifecycle_mixin import WidgetLifecycleMixin


class EvaluationRole(IntEnum):
    EvaluationId = Qt.ItemDataRole.UserRole + 1


class PartialPlaceholderListWidget(QListWidget, WidgetLifecycleMixin):

    def __init__(self, placeholder_text="", parent: QWidget | None = None):
        super().__init__(parent)
        self._placeholder_text = placeholder_text

    @override
    def _create_widgets(self) -> None:
        self.setWordWrap(True)
        self.setTextElideMode(Qt.TextElideMode.ElideNone) # type: ignore[arg-type]
        self.setResizeMode(QListView.ResizeMode.Adjust) # type: ignore[arg-type]
        self.setUniformItemSizes(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # type: ignore[arg-type]

    def set_placeholder_text(self, text: str) -> None:
        self._placeholder_text = text
        self.viewport().update()

    @override
    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)

        if self.count() == 0 and self._placeholder_text:
            painter = QPainter(self.viewport())

            painter.setPen(self.palette().text().color())
            painter.setOpacity(0.5)

            rect = self.viewport().rect()
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, self._placeholder_text)


class PartialFilterListWidget(QListWidget, WidgetLifecycleMixin):
    _is_final_component = True

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self.setFlow(QListWidget.Flow.LeftToRight) # type: ignore[arg-type]
        self.setWrapping(True)
        self.setResizeMode(QListWidget.ResizeMode.Adjust) # type: ignore[arg-type]
        self.setTextElideMode(Qt.TextElideMode.ElideNone) # type: ignore[arg-type]
        self.setUniformItemSizes(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # type: ignore[arg-type]
        self.setSpacing(9)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed) # type: ignore[arg-type]

    def update_filters(self, widget_items: list[WidgetItem]):
        self.blockSignals(True)
        self.clear()

        for widget_item in widget_items:
            item = QListWidgetItem(widget_item.label)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked) # type: ignore[arg-type]
            item.setData(EvaluationRole.EvaluationId, widget_item.internal_value)
            self.addItem(item)

        self.blockSignals(False)

    def clear_selection(self):
        for index in range(self.count()):
            item = self.item(index)
            item.setCheckState(Qt.CheckState.Unchecked) # type: ignore[arg-type]

    def _on_filter_changed(self, item: QListWidgetItem) -> None:
        # Each list must emit its own signal. The connect signal cannot be implemented in this class, as it
        # binds the base class to the signal and emit twice the child class signal.
        raise NotImplementedError("The child class must override this method.")

    @override
    def sizeHint(self) -> QSize:
        if self.count() == 0:
            return super().sizeHint()

        self.doItemsLayout()
        last_item = self.item(self.count() - 1)
        item_rect = self.visualItemRect(last_item)
        total_height = item_rect.bottom() + self.spacing()

        return QSize(super().sizeHint().width(), total_height)

    @override
    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.updateGeometry()

