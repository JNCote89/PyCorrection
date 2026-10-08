from pathlib import Path
from typing import override

from PySide6.QtCore import QStandardPaths, Qt, Slot
from PySide6.QtGui import QDragEnterEvent, QDragLeaveEvent, QDropEvent
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout, QWidget

from src.py_correction.core import nuitka_helpers
from src.py_correction.ui.components.base_components.widget_lifecycle_mixin import WidgetLifecycleMixin
from src.py_correction.ui.components.default_widgets.message_boxes import DefaultQuestionMessageBox
from src.py_correction.ui.feedbacks.messages.confirmation_messages import BatchFileImportVerificationMessage


class PartialDragAndDropWidget(QWidget, WidgetLifecycleMixin):
    def __init__(self, label: str, extensions: tuple, file_dialog_window_title: str,
                 allow_multiple: bool = False, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._label = label

        self._extensions = extensions
        # Qt filters based on space, not comma
        self._extension_qt_filter = f"(*{' *'.join(self._extensions)})"

        self._file_dialog_window_title = file_dialog_window_title
        self._starting_directory = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DocumentsLocation) # type: ignore[arg-type]
        self._allow_multiple = allow_multiple

    @override
    def _create_widgets(self) -> None:
        self.setMinimumHeight(150)
        self.drag_drop_container = QWidget()
        self.drag_drop_container.setObjectName("DragDropContainer")
        # Note: QSS use C++ bool -> [dragging="true"]
        self.drag_drop_container.setProperty("dragging", False)

        self.drag_browse_button = QPushButton("Sélectionner à partir du navigateur")
        self.drag_browse_button.setObjectName("DragBrowseButton")
        nuitka_helpers.safe_connect(signal=self.drag_browse_button.clicked, slot=self._open_file_dialog_from_button)

        self.drag_label = QLabel(self._label)
        self.drag_label.setAlignment(Qt.AlignmentFlag.AlignCenter) # type: ignore[arg-type]
        self.drag_label.setObjectName("DragBrowseLabel")

        self.setAcceptDrops(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred) # type: ignore[arg-type]

    @override
    def _assemble_layout(self) -> None:
        main_layout = QVBoxLayout(self)

        container_layout = QVBoxLayout(self.drag_drop_container)
        container_layout.setContentsMargins(15, 15, 15, 25)

        top_row_layout = QHBoxLayout()
        top_row_layout.addWidget(self.drag_browse_button)
        top_row_layout.addStretch()

        container_layout.addLayout(top_row_layout)
        container_layout.addWidget(self.drag_label, stretch=1)

        main_layout.addWidget(self.drag_drop_container)

    def update_starting_path_directory(self, path_directory: Path) -> None:
        self._starting_directory = path_directory

    def _process_import_file(self, file_path: Path) -> None:
        raise NotImplementedError("The child class must implement a method to process the imported file.")

    @override
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()

            if not self._allow_multiple and len(urls) > 1:
                event.ignore()
                return

            valid_files = [url.toLocalFile() for url in urls if url.toLocalFile().endswith(self._extensions)]

            if valid_files and len(valid_files) == len(urls):
                event.acceptProposedAction()
                self._update_dragging_style(True)
                return
        event.ignore()

    @override
    def dragLeaveEvent(self, event: QDragLeaveEvent) -> None:
        self._update_dragging_style(False)
        event.accept()

    @override
    def dropEvent(self, event: QDropEvent) -> None:
        event.acceptProposedAction()
        self._update_dragging_style(False)

        file_paths = [Path(url.toLocalFile()) for url in event.mimeData().urls()]
        self._handle_file_selection(file_paths)

    @Slot()
    def _open_file_dialog_from_button(self) -> None:
        if self._allow_multiple:
            file_paths, _ = QFileDialog.getOpenFileNames(self, self._file_dialog_window_title,
                                                         str(self._starting_directory), self._extension_qt_filter)
            file_paths = [Path(file_path) for file_path in file_paths]

        else:
            file_path, _ = QFileDialog.getOpenFileName(self, self._file_dialog_window_title,
                                                       str(self._starting_directory), self._extension_qt_filter)
            file_paths = [Path(file_path)] if file_path else []

        if file_paths:
            self._handle_file_selection(file_paths)

    def _update_dragging_style(self, dragging: bool) -> None:
        self.drag_drop_container.setProperty("dragging", dragging)

        self.style().unpolish(self.drag_drop_container)
        self.style().polish(self.drag_drop_container)

    def _handle_file_selection(self, file_paths: list[Path]) -> None:

        import_confirmation_message = BatchFileImportVerificationMessage(imported_paths=file_paths)
        message_box = DefaultQuestionMessageBox(window_title=import_confirmation_message.title,
                                                html_message=import_confirmation_message.html_text,
                                                parent=self)
        if message_box.get_reply_bool():
            for file_path in file_paths:
                self._process_import_file(file_path=file_path)

