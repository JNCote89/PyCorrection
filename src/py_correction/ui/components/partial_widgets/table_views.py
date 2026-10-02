from typing import override

from PySide6.QtCore import QAbstractTableModel, QRect, QSize, QSortFilterProxyModel, QTimer, Qt
from PySide6.QtGui import QResizeEvent, QShowEvent
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableView, QWidget

from src.py_correction.ui.components.base_components.widget_lifecycle_mixin import WidgetLifecycleMixin


class PartialReactiveTableView(QTableView, WidgetLifecycleMixin):
    def __init__(self, table_model: QAbstractTableModel, column_index_stretch: int | None = None,
                 interactive: bool = True, parent=None):
        super().__init__(parent=parent)
        self._column_index_stretch = column_index_stretch
        self._interactive = interactive
        self.table_model = table_model
        self.proxy_model = QSortFilterProxyModel()

    @override
    def _create_widgets(self) -> None:
        self._setup_models()
        self._configure_table_behavior()
        self._configure_table_sorting()

        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows) # type: ignore[arg-type]
        self.horizontalHeader().setHighlightSections(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn) # type: ignore[arg-type]
        self._horizontal_scrollbar_height = self.horizontalScrollBar().sizeHint().height()
        self.setViewportMargins(0, 0, 0, self._horizontal_scrollbar_height)

    def refresh_table(self) -> None:
        self._configure_headers()

        # ToDo : Refactor to properly calculate the viewport instead of hacking the stretch method.
        if self._interactive:
            QTimer.singleShot(0, self._make_interactive)

    def adjust_table_height(self):
        # Method to avoid having a double scrolling bar. Delegate the responsibility of scrolling only on the pages.
        # Calculate the total table height to fit the data on the fly.
        model = self.model()
        if not model:
            return

        total_height = self.horizontalHeader().height()
        for row in range(model.rowCount()):
            total_height += self.rowHeight(row)

        total_height += 6 + self._horizontal_scrollbar_height

        self.setFixedHeight(total_height)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # type: ignore[arg-type]

    def _configure_table_sorting(self) -> None:
        """To be configured if needed in the child class"""
        ...

    def _setup_models(self) -> None:
        self.proxy_model.setSourceModel(self.table_model)
        self.setModel(self.proxy_model)

    def _configure_table_behavior(self) -> None:
        self.setSortingEnabled(True)

    def _configure_headers(self) -> None:
        self.verticalHeader().setVisible(False)
        header = self.horizontalHeader()

        if self._column_index_stretch:
            header.setSectionResizeMode(self._column_index_stretch, QHeaderView.ResizeMode.Stretch) # type: ignore[arg-type]
            for col_index in range(header.count()): # type: ignore[arg-type]
                if col_index != self._column_index_stretch:
                    header.setSectionResizeMode(col_index, QHeaderView.ResizeMode.ResizeToContents) # type: ignore[arg-type]
        else:
            header.setStretchLastSection(True)
            self.resizeColumnsToContents()

    def _make_interactive(self) -> None:
        header = self.horizontalHeader()
        for col_index in range(header.count()):  # type: ignore
            header.setSectionResizeMode(col_index, QHeaderView.ResizeMode.Interactive) # type: ignore[arg-type]

    @override
    def showEvent(self, event: QShowEvent):
        super().showEvent(event)

        # To avoid the table collapsing when the app starts on another page. It gives time to Qt to recalculate
        # the geometry properly.
        QTimer.singleShot(0, self.refresh_table)


class ProportionalHeaderView(QHeaderView):
    def __init__(self, orientation: Qt.Orientation, parent: QWidget | None = None):
        super().__init__(orientation, parent=parent)
        self.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag(Qt.TextFlag.TextWordWrap)) # type: ignore[arg-type]

    @override
    def sectionSizeFromContents(self, logical_index: int) -> QSize:
        text = self.model().headerData(logical_index, self.orientation(), Qt.ItemDataRole.DisplayRole)
        if not text:
            return super().sectionSizeFromContents(logical_index)

        max_width = max(self.sectionSize(logical_index) - 6, 10)

        font_metrics = self.fontMetrics()
        rect = font_metrics.boundingRect(QRect(0, 0, max_width, 1000), int(self.defaultAlignment()), str(text))

        return QSize(max_width + 6, rect.height() + 12)


class PartialFixTableView(QTableView, WidgetLifecycleMixin):
    """Shortcut to navigate
    Tab/ shift + tab (adjacent rows)
    Space to edit
    Escape to cancel
    Enter to commit
    """

    def __init__(self, column_ratios: list[int], table_model: QAbstractTableModel, cell_font_size: int = 10,
                 padding: int = 6, title_font_size: int = 11, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._column_ratios = column_ratios
        self.table_model = table_model
        self._cell_font_size = cell_font_size
        self._padding = padding
        self._title_font_size = title_font_size

    @override
    def _create_widgets(self) -> None:
        self._setup_models()
        self._configure_headers()

        self.setWordWrap(True)

        self.setStyleSheet(f"QTableView {{ font-size: {self._cell_font_size}pt; }} "
                           f"QTableView::item {{ padding: {self._padding}px;}}""")

        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setHighlightSections(False)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus) # type: ignore[arg-type]
        self.setTabKeyNavigation(True)

    def adjust_table_height(self):
        # Method to avoid having a double scrolling bar. Delegate the responsibility of scrolling only on the pages.
        # Calculate the total table height to fit the data on the fly.

        model = self.model()
        if not model or model.rowCount() == 0:
            self.setFixedHeight(self.horizontalHeader().sizeHint().height())
            return

        total_height = 0
        if self.horizontalHeader().isVisible():
            total_height += self.horizontalHeader().sizeHint().height()

        for row in range(model.rowCount()):
            total_height += self.rowHeight(row)

        if self.horizontalScrollBar().isVisible():
            total_height += self.horizontalScrollBar().height()

        margins = self.contentsMargins()
        total_height += margins.top() + margins.bottom() + (self.frameWidth() * 2)

        self.setFixedHeight(total_height)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # type: ignore[arg-type]

    def _setup_models(self) -> None:
        self.setModel(self.table_model)

    def _configure_headers(self) -> None:
        self.verticalHeader().setVisible(False)

        self.custom_header = ProportionalHeaderView(Qt.Orientation.Horizontal, self) # type: ignore[arg-type]
        self.setHorizontalHeader(self.custom_header)
        self.custom_header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive) # type: ignore[arg-type]
        self.custom_header.setStyleSheet(f"QHeaderView::section {{font-size: {self._title_font_size}pt;"
                                         f" padding: {self._padding}px}}")

    def _update_row_heights_from_widgets(self) -> None:
        model = self.model()
        if not model:
            return

        horizontal_padding = (self._padding * 2) + 2

        for row in range(model.rowCount()):
            max_height = self.verticalHeader().defaultSectionSize()

            for col in range(model.columnCount()):
                index = model.index(row, col)
                widget = self.indexWidget(index)
                if widget:
                    col_width = self.columnWidth(col)
                    effective_text_width = max(1, col_width - horizontal_padding)

                    widget.setFixedWidth(effective_text_width)

                    hint_height = widget.heightForWidth(effective_text_width)
                    if hint_height <= 0:
                        hint_height = widget.sizeHint().height()

                    max_height = max(max_height, hint_height + (self._padding * 2)) + 2

            # Some ComboBox delegates does not return the correct size hint, quick hack to ensure the options have
            # enough room to be display. At the moment, the injected QLabel is dictating the size.
            # ToDo fix the size hint return by the ComboBox delegates
            minimum_row_size = 90
            if max_height > minimum_row_size:
                self.setRowHeight(row, max_height)
            else:
                self.setRowHeight(row, minimum_row_size)

    @override
    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)

        self.blockSignals(True)

        total_width = self.viewport().width()
        total_ratio = sum(self._column_ratios)

        for i, weight in enumerate(self._column_ratios):
            col_width = int(total_width * (weight / total_ratio))
            self.setColumnWidth(i, col_width)

        self.custom_header.headerDataChanged(Qt.Orientation.Horizontal, 0, len(self._column_ratios) - 1) # type: ignore[arg-type]

        self._update_row_heights_from_widgets()

        self.blockSignals(False)

        self.adjust_table_height()