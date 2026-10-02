from typing import override

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSplitter, QWidget

from src.py_correction.ui.components.base_components.widget_lifecycle_mixin import WidgetLifecycleMixin


class DefaultHalfSplitter(QSplitter, WidgetLifecycleMixin):
    _is_final_component = True

    def __init__(self, first_widget: QWidget, second_widget: QWidget,
                 orientation: Qt.Orientation = Qt.Orientation.Horizontal, # type: ignore[arg-type]
                 splitter_sizes: list[int] | None = None,
                 collapsible: bool = False, parent=None):
        super().__init__(orientation=orientation, parent=parent)
        self._first_widget = first_widget
        self._second_widget = second_widget
        self._splitter_sizes = splitter_sizes or [200, 800]
        self._collapsible = collapsible

        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self.addWidget(self._first_widget)
        self.addWidget(self._second_widget)

        self.setCollapsible(0, self._collapsible)
        self.setCollapsible(1, self._collapsible)
        self.setStretchFactor(0, 0)
        self.setStretchFactor(1, 1)
        self.setSizes(self._splitter_sizes)
