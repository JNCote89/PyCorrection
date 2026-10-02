from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtWidgets import QFormLayout, QGridLayout, QTableView, QVBoxLayout, QWidget

from src.py_correction.ui.components.default_widgets.scroll_area import DefaultScrollArea


class DefaultGridLayout(QGridLayout):
    # The QSS properties do not work consistently
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setVerticalSpacing(24)
        self.setHorizontalSpacing(12)
        self.setContentsMargins(12, 12, 12, 12)


class DefaultFormLayout(QFormLayout):
    # The QSS properties do not work consistently
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setVerticalSpacing(24)
        self.setHorizontalSpacing(12)
        self.setContentsMargins(12, 12, 12, 12)
        self.setRowWrapPolicy(QFormLayout.WrapLongRows)  # type: ignore
        self.setLabelAlignment(Qt.AlignmentFlag.AlignRight)  # type: ignore


class DefaultPageVerticalScrollLayout(QWidget):
    def __init__(self, page_view: QWidget, widgets: list[QWidget], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.widgets = widgets

        self.page_layout = QVBoxLayout(page_view)
        self.widget_layout = self._create_widgets_layout()

        self.scroll_area = DefaultScrollArea(widget_layout=self.widget_layout)
        self.page_layout.addWidget(self.scroll_area)

        # Wire scroll syncing locally, including nested tables inside GroupBoxes
        self._connect_table_views()

    def _connect_table_views(self) -> None:
        for top_widget in self.widgets:
            nested_tables = top_widget.findChildren(QTableView)

            if isinstance(top_widget, QTableView):
                nested_tables.append(top_widget)

            for table in nested_tables:
                table.selectionModel().currentChanged.connect(
                    lambda current, prev, t=table: self._sync_scroll_area(t, current))

    def _sync_scroll_area(self, table: QTableView, current_index: QModelIndex) -> None:
        if not current_index.isValid():
            return

        cell_rect = table.visualRect(current_index)

        cell_bottom_left = cell_rect.bottomLeft()

        bottom_in_container = table.mapTo(self.scroll_area.container, cell_bottom_left)

        bottom_padding = 210

        self.scroll_area.ensureVisible(bottom_in_container.x(), bottom_in_container.y(), # type: ignore[arg-type]
                                       xmargin=0, ymargin=bottom_padding)

    def _create_widgets_layout(self) -> QVBoxLayout:
        widget_layout = QVBoxLayout()
        widget_layout.setSpacing(30)
        widget_layout.setContentsMargins(12, 12, 12, 12)

        for widget in self.widgets:
            widget_layout.addWidget(widget)

        widget_layout.addStretch()
        return widget_layout
