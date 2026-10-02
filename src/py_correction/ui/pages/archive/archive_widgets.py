from pathlib import Path
from typing import override

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from src.py_correction.ui.components.partial_widgets.import_widgets import PartialDragAndDropWidget


class RestoredArchiveImportWidget(PartialDragAndDropWidget):
    _is_final_component = True

    restoredArchivePathSubmitted = Signal(Path)

    LABEL = "ou glisser le fichier .zip du cours à restaurer."
    EXTENSIONS = (".zip", ".db")
    FILE_DIALOG_WINDOW_TITLE = "Sélectionner le dossier .zip à restaurer"

    def __init__(self, parent: QWidget | None = None):
        super().__init__(label=self.LABEL, extensions=self.EXTENSIONS,
                         file_dialog_window_title=self.FILE_DIALOG_WINDOW_TITLE, allow_multiple=False,
                         parent=parent)
        self._init_ui()

    @override
    def _process_import_file(self, file_path: Path) -> None:
        file_path = Path(file_path)
        self.restoredArchivePathSubmitted.emit(file_path)
