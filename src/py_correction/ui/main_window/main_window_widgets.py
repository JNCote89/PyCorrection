from typing import TYPE_CHECKING, override

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import QListView, QListWidget, QListWidgetItem, QStackedWidget, QVBoxLayout, QWidget

from src.py_correction.ui.components.base_components.widget_lifecycle_mixin import WidgetLifecycleMixin
from src.py_correction.ui.components.partial_widgets.log_console import PartialLogConsoleWidget

if TYPE_CHECKING:
    from src.py_correction.ui.registries.page_registry import PageRegistry


class PagesStackedWidget(QStackedWidget, WidgetLifecycleMixin):
    _is_final_component = True

    def __init__(self, page_registry: type["PageRegistry"],
                 initial_page_label: str | None, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._page_registry = page_registry
        self._initial_page_label = initial_page_label

        self._page_labels = []

        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        widgets = self._init_page_instances()

        for widget_instance in widgets:
            self.addWidget(widget_instance)

        self.setCurrentIndex(self.initial_page_index)

    @property
    def initial_page_index(self) -> int:
        """Calculate the index of the initial page specified in the user settings file for the SidebarListWidget."""
        if self._page_registry.from_label(self._initial_page_label) is not None:
            initial_page = self.findChild(QWidget, self._initial_page_label)  # type: ignore[arg-type]
            return self.indexOf(initial_page)  # type: ignore[arg-type]

        return 0

    @property
    def page_labels(self) -> list[str]:
        """Return the list of page labels used to populate the SidebarListWidget."""
        return self._page_labels

    @page_labels.setter
    def page_labels(self, page_labels: list[str]) -> None:
        self._page_labels = page_labels

    def _init_page_instances(self) -> list[QWidget]:
        widgets = []
        labels = []

        for page in self._page_registry:
            page_widget = page.widget_class()
            page_label = page.label

            page_widget.setObjectName(page_label)
            widgets.append(page_widget)
            labels.append(page_label)

        self._page_labels.extend(labels)
        return widgets


class SidebarListWidget(QListWidget, WidgetLifecycleMixin):
    """Manage navigation for the pages in a list and receives the index from the PagesStackedWidget"""
    _is_final_component = True

    def __init__(self, labels: list[str], initial_page_index: int, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._labels = labels
        self._initial_page_index = initial_page_index

        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self.setWordWrap(True)
        self.setTextElideMode(Qt.TextElideMode.ElideNone) # type: ignore[arg-type]
        self.setResizeMode(QListView.ResizeMode.Adjust) # type: ignore[arg-type]
        self.setUniformItemSizes(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # type: ignore[arg-type]
        self.setMinimumWidth(250)

        for label in self._labels:
            self.addItem(QListWidgetItem(label))

        self.setCurrentRow(self._initial_page_index)

    @override
    def resizeEvent(self, event: QResizeEvent) -> None:
        """
        Quick hack to bypass the ellipsis glitch when resizing the window. The geometry calculation is wrong in some
        configurations, so Qt does not know how to wrap the text. Giving 60 px makes enough room to wrap 2 lines
        without precise calculation. The padding might have to change depending on the font use.
        """
        # Todo : Write a function to properly calculate the font geometry, so the wrapping works in every configuration.
        super().resizeEvent(event)

        for i in range(self.count()):  # type: ignore
            item = self.item(i)
            item.setSizeHint(QSize(self.viewport().width(), 60))


class ConsoleWidget(PartialLogConsoleWidget):
    """Fix console at the bottom of the main window to log user notifications."""
    _is_final_component = True

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self.setFixedHeight(150)


class WorkAreaContainer(QWidget, WidgetLifecycleMixin):
    """Area beside the vertical sidebar"""
    _is_final_component = True

    def __init__(self, page_stacked_widget: PagesStackedWidget, console_widget: ConsoleWidget,
                 parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._page_stacked_widget = page_stacked_widget
        self._console_widget = console_widget

        self._init_ui()

    @override
    def _assemble_layout(self) -> None:
        main_layout = QVBoxLayout()
        main_layout.addWidget(self._page_stacked_widget)
        main_layout.addWidget(self._console_widget)
        self.setLayout(main_layout)
