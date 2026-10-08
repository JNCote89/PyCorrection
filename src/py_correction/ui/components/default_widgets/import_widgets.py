from pathlib import Path
from typing import override

from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLineEdit, QStyle, QWidget

from src.py_correction.core import nuitka_helpers
from src.py_correction.ui.components.base_components.widget_lifecycle_mixin import WidgetLifecycleMixin


class DefaultPathPickerWidget(QWidget, WidgetLifecycleMixin):
    _is_final_component = True

    userRootDirectoryChanged = Signal(Path)

    def __init__(self, parent:QWidget | None = None):
        super().__init__(parent)
        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self.path_directory_line_edit = QLineEdit()
        self.path_directory_line_edit.setReadOnly(True)

        folder_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton)  # type: ignore[arg-type]

        browse_action = QAction(folder_icon, "Navigation", self.path_directory_line_edit)
        nuitka_helpers.safe_connect(signal=browse_action.triggered, slot=self._browse_directory)
        self.path_directory_line_edit.addAction(browse_action, QLineEdit.ActionPosition.LeadingPosition)  # type: ignore[arg-type]

    @override
    def _assemble_layout(self) -> None:
        layout = QHBoxLayout(self)
        layout.addWidget(self.path_directory_line_edit)
        self.setLayout(layout)

    def update_path_directory(self, path_directory: Path) -> None:
        self.path_directory_line_edit.setText(str(path_directory))

    @Slot()
    def _browse_directory(self) -> None:
        current_directory = self.path_directory_line_edit.text()
        dir_path = QFileDialog.getExistingDirectory(self, "Sélectionner un répertoire racine",
                                                    current_directory)
        if dir_path:
            self.userRootDirectoryChanged.emit(dir_path)
