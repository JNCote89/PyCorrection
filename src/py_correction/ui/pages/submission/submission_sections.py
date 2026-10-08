from pathlib import Path
from typing import override

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QGroupBox, QPushButton, QWidget

from src.py_correction.core import nuitka_helpers
from src.py_correction.core.domains.shared.shared_dtos import ComboBoxPayload
from src.py_correction.ui.components.base_components.widget_lifecycle_mixin import WidgetLifecycleMixin
from src.py_correction.ui.components.default_widgets.labels import DefaultDynamicLabel, DefaultLabel
from src.py_correction.ui.components.layouts import DefaultGridLayout
from src.py_correction.ui.components.shared_components.evaluation_selection.evaluation_selection_widgets import (
    EvaluationIDComboBox)
from src.py_correction.ui.feedbacks.labels.directory_labels import (SubmissionCountLabelText, TemplateFilenameLabelText)
from src.py_correction.ui.pages.submission.submission_widgets import MoodleSubmissionsImportWidget


class SubmissionsManagementGroupBox(QGroupBox, WidgetLifecycleMixin):
    _is_final_component = True

    evaluationIDChanged = Signal(object)
    moodleZipFileSubmitted = Signal(Path)
    makeStudentCorrectionButtonClicked = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__("Importation des remises et génération des grilles de correction pour chaque étudiant",
                         parent=parent)
        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self._evaluation_selection_label = DefaultLabel(text="Sélectionner une évaluation")
        self._evaluation_combo_box = EvaluationIDComboBox()

        self._moodle_import_label = DefaultLabel(text="Importer les travaux remis")
        self._moodle_import_widget = MoodleSubmissionsImportWidget()

        self._check_import_parameters_label = DefaultLabel(text="Vérifier les paramètres de génération des grilles "
                                                                "de correction étudiantes",
                                                           subtext="Un gabarit de correction doit être associé et "
                                                                   "des travaux doivent être importés")
        self._template_filename_label = DefaultDynamicLabel(TemplateFilenameLabelText().label_text)
        self._submission_count_label = DefaultDynamicLabel(SubmissionCountLabelText().label_text)

        self._make_student_correction_file_label = DefaultLabel(text="Générer les grilles de corrections pour chaque "
                                                                     "étudiant")
        self._make_student_correction_file_button = QPushButton("Générer les grilles de correction")

    @override
    def _assemble_layout(self) -> None:
        main_grid_layout = DefaultGridLayout(self)

        main_grid_layout.addWidget(self._evaluation_selection_label, 0, 0)
        main_grid_layout.addWidget(self._evaluation_combo_box, 0, 1)

        main_grid_layout.addWidget(self._moodle_import_label, 1, 0, 2, 1)
        main_grid_layout.addWidget(self._moodle_import_widget, 1, 1, 2, 1)

        main_grid_layout.addWidget(self._check_import_parameters_label, 3, 0, 2, 1)
        main_grid_layout.addWidget(self._template_filename_label, 3, 1, 1, 1)
        main_grid_layout.addWidget(self._submission_count_label, 4, 1, 1, 1)

        main_grid_layout.addWidget(self._make_student_correction_file_label, 5, 0)
        main_grid_layout.addWidget(self._make_student_correction_file_button, 5, 1, 1, 1)

        main_grid_layout.setColumnStretch(0, 1)
        main_grid_layout.setColumnStretch(1, 3)

    @override
    def _connect_downstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._evaluation_combo_box.evaluationIDChanged,
                                    slot=self.evaluationIDChanged)
        nuitka_helpers.safe_connect(signal=self._moodle_import_widget.zipFileSubmitted,
                                    slot=self.moodleZipFileSubmitted)
        nuitka_helpers.safe_connect(signal=self._make_student_correction_file_button.clicked,
                                    slot=self.makeStudentCorrectionButtonClicked)

    @Slot(ComboBoxPayload)
    def populate_evaluation_id_combo_box(self, payload: ComboBoxPayload) -> None:
        self._evaluation_combo_box.populate_combo_box(payload=payload)

    @Slot(int)
    def synchronized_evaluation_id(self, evaluation_id: int | None) -> None:
        self._evaluation_combo_box.synchronized_evaluation_id(evaluation_id=evaluation_id)

    @Slot(TemplateFilenameLabelText)
    def update_template_filename_label(self, label_text: TemplateFilenameLabelText) -> None:
        self._template_filename_label.setText(label_text.label_text)

    @Slot(SubmissionCountLabelText)
    def update_submission_count_label(self, label_text: SubmissionCountLabelText) -> None:
        self._submission_count_label.setText(label_text.label_text)

    @Slot(bool)
    def update_make_student_correction_file_button(self, state: bool) -> None:
        self._make_student_correction_file_button.setEnabled(state)
