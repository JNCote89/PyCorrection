from pathlib import Path
from typing import override

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from src.py_correction.ui.components.partial_widgets.import_widgets import PartialDragAndDropWidget


class MoodleSubmissionsImportWidget(PartialDragAndDropWidget):
    _is_final_component = True

    zipFileSubmitted = Signal(Path)

    _LABEL = "ou glisser le fichier .zip des travaux remis dans des dossiers en provenance de Moodle"
    _EXTENSIONS = (".zip",)
    _FILE_DIALOG_WINDOW_TITLE = ("Sélectionner le fichier .zip des travaux remis dans des dossiers en provenance de"
                                 " Moodle")

    def __init__(self, parent: QWidget | None = None):
        super().__init__(label=self._LABEL, extensions=self._EXTENSIONS,
                         file_dialog_window_title=self._FILE_DIALOG_WINDOW_TITLE, allow_multiple=False,
                         parent=parent)
        self._init_ui()

    @override
    def _process_import_file(self, file_path: Path) -> None:
        self.zipFileSubmitted.emit(file_path)
