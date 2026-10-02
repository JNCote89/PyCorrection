from typing import override

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QMainWindow, QWidget

from src.py_correction.core.dependency_injection import container
from src.py_correction.ui.components.default_widgets.splitters import DefaultHalfSplitter
from src.py_correction.ui.main_window.main_window_controller import MainWindowController
from src.py_correction.ui.main_window.main_window_widgets import (ConsoleWidget, PagesStackedWidget, SidebarListWidget,
                                                                  WorkAreaContainer)
from src.py_correction.ui.registries.page_registry import PageRegistry


class MainWindow(QMainWindow):
    PAGE_REGISTRY = PageRegistry

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._init_ui()

        self._worker_registry = container.worker_registry()

    def _init_ui(self) -> None:
        self._initialize_controllers()
        self._set_main_window()
        self._create_widgets()
        self._assemble_layout()
        self._connect_internal_signals()

    def _initialize_controllers(self):
        self._page_controller = MainWindowController()

    def _set_main_window(self) -> None:
        self.setWindowTitle("PyCorrection")
        self.setMinimumSize(600, 400)

        window_size = self._page_controller.window_size

        if not window_size:
            self.showMaximized()
        else:
            self.resize(window_size)

    def _create_widgets(self) -> None:
        self._pages_stacked_widget = PagesStackedWidget(
            page_registry=self.PAGE_REGISTRY,
            initial_page_label=self._page_controller.restored_page_label_selected)

        self._sidebar_list_widget = SidebarListWidget(
            labels=self._pages_stacked_widget.page_labels,
            initial_page_index=self._pages_stacked_widget.initial_page_index)

        self._console_widget = ConsoleWidget()

    def _assemble_layout(self) -> None:
        self._work_area_container = WorkAreaContainer(page_stacked_widget=self._pages_stacked_widget,
                                                      console_widget=self._console_widget)
        self._splitter = DefaultHalfSplitter(
            orientation=Qt.Orientation.Horizontal,  # type: ignore
            first_widget=self._sidebar_list_widget,
            second_widget=self._work_area_container,
            splitter_sizes=self._page_controller.restored_main_splitter_sizes)

        self.setCentralWidget(self._splitter)

    def _connect_internal_signals(self) -> None:
        self._sidebar_list_widget.currentRowChanged.connect(self._pages_stacked_widget.setCurrentIndex)

    @override
    def closeEvent(self, event: QCloseEvent) -> None:
        self._worker_registry.cancel_all()
        self._worker_registry.wait_all(msecs=1000)

        # Signal on close event can cause async bugs, keep the save method inside the closeEvent Qt method.
        self._page_controller.save_settings(
            window_width=self.width(), window_height=self.height(), splitter_sizes=self._splitter.sizes(),
            page_label_selected=self._pages_stacked_widget.currentWidget().objectName())
        super().closeEvent(event)
