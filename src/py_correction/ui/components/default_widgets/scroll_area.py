from typing import override

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLayout, QScrollArea, QWidget

from src.py_correction.ui.components.base_components.widget_lifecycle_mixin import WidgetLifecycleMixin


class DefaultScrollArea(QScrollArea, WidgetLifecycleMixin):
    _is_final_component = True

    def __init__(self, widget_layout: QLayout, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._widget_layout = widget_layout

        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)  # type: ignore[arg-type]
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # type: ignore[arg-type]

    @override
    def _assemble_layout(self) -> None:
        self.container = QWidget()
        self.container.setLayout(self._widget_layout)
        self.setWidget(self.container)
