from pathlib import Path
from typing import override

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGroupBox, QPushButton, QWidget

from src.py_correction.ui.components.base_components.widget_lifecycle_mixin import WidgetLifecycleMixin
from src.py_correction.ui.components.default_widgets.labels import DefaultDynamicLabel, DefaultLabel
from src.py_correction.ui.components.layouts import DefaultGridLayout
from src.py_correction.ui.feedbacks.labels.directory_labels import ArchivePathLabelText
from src.py_correction.ui.pages.archive.archive_widgets import RestoredArchiveImportWidget


class ArchiveManagementGroupBox(QGroupBox, WidgetLifecycleMixin):
    _is_final_component = True

    archiveButtonClicked = Signal()
    restoredArchivePathSubmitted = Signal(Path)

    def __init__(self, parent: QWidget | None = None):
        super().__init__("Gestion de l'archivage", parent=parent)

        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self._archive_label = DefaultLabel(text="Archivage de cours",
                                           subtext="Le cours sera retiré de l'application et tous les dossiers seront "
                                                   "compressés dans le répertoire des archives")

        self._archive_button = QPushButton("Archiver le cours sélectionné")

        self._restored_archive_label = DefaultLabel(text="Restaurer un cours archivé")
        self._restored_archive_import_widget = RestoredArchiveImportWidget()

        self._delete_archive_label = DefaultLabel(text="Supprimer un cours",
                                                  subtext="Pour supprimer définitivement un cours, vous devez "
                                                          "sélectionner le cours archivé dans le répertoire des "
                                                          "archives et le supprimer de votre système manuellement")

        self._delete_archive_directory_label = DefaultDynamicLabel()

    @override
    def _assemble_layout(self) -> None:
        main_grid_layout = DefaultGridLayout(self)

        main_grid_layout.addWidget(self._archive_label, 0, 0)
        main_grid_layout.addWidget(self._archive_button, 0, 1)

        main_grid_layout.addWidget(self._restored_archive_label, 1, 0)
        main_grid_layout.addWidget(self._restored_archive_import_widget, 1, 1)

        main_grid_layout.addWidget(self._delete_archive_label, 2, 0)
        main_grid_layout.addWidget(self._delete_archive_directory_label, 2, 1)

        main_grid_layout.setColumnStretch(0, 1)
        main_grid_layout.setColumnStretch(1, 3)

    @override
    def _connect_downstream_signals(self) -> None:
        self._archive_button.clicked.connect(self.archiveButtonClicked)
        self._restored_archive_import_widget.restoredArchivePathSubmitted.connect(self.restoredArchivePathSubmitted)

    def set_archive_label(self, label_text: ArchivePathLabelText) -> None:
        self._delete_archive_directory_label.setText(label_text.label_text)

    def set_archive_button_state(self, button_state: bool) -> None:
        self._archive_button.setEnabled(button_state)
