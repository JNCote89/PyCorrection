from pathlib import Path
from typing import override

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QGroupBox, QPushButton, QScrollArea, QVBoxLayout, QWidget

from src.py_correction.core import nuitka_helpers
from src.py_correction.core.domains.reference.reference_figures_dtos import GradeReferencePlotDTO
from src.py_correction.core.domains.shared.shared_dtos import ComboBoxPayload
from src.py_correction.core.theme_manager import ThemeOptions
from src.py_correction.ui.components.base_components.widget_lifecycle_mixin import WidgetLifecycleMixin
from src.py_correction.ui.components.default_widgets.labels import (DefaultDynamicLabel, DefaultLabel)
from src.py_correction.ui.components.layouts import DefaultGridLayout
from src.py_correction.ui.components.shared_components.evaluation_selection.evaluation_selection_widgets import (
    EvaluationIDComboBox)
from src.py_correction.ui.feedbacks.labels.directory_labels import (GeNoteLabelText, MoodleCorrectionArchiveLabelText)
from src.py_correction.ui.pages.grade.grade_widgets import ReferenceGradePlotChart


class GradeManagementGroupBox(QGroupBox, WidgetLifecycleMixin):
    _is_final_component = True

    evaluationIDChanged = Signal(object)
    moodleArchiveButtonClicked = Signal()
    genoteUpdateButtonClicked = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__("Gestion de la rétroaction et des notes", parent=parent)
        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self._evaluation_selection_label = DefaultLabel(text="Sélectionner une évaluation",
                                                        alignment_h_flag=Qt.AlignmentFlag.AlignHCenter) # type: ignore[arg-type]
        self._evaluation_combo_box = EvaluationIDComboBox()

        self._genote_update_label = DefaultLabel(text="Compiler les notes des étudiants dans la feuille Excel GeNote")
        self._genote_update_button = QPushButton("Mettre à jour le fichier GeNote")
        self._genote_update_button.setEnabled(False)

        self._genote_update_file_path_label = DefaultDynamicLabel(GeNoteLabelText().label_text)

        self._moodle_correction_label = DefaultLabel(text="Compresser les fichiers de correction pour les "
                                                          "déposer en lot sur Moodle")
        self._moodle_correction_archive_button = QPushButton("Générer le fichier .zip de rétroaction pour Moodle")
        self._moodle_correction_archive_button.setEnabled(False)

        self._moodle_correction_archive_path_label = DefaultDynamicLabel(MoodleCorrectionArchiveLabelText().label_text)

    @override
    def _assemble_layout(self) -> None:
        main_grid_layout = DefaultGridLayout(self)

        main_grid_layout.addWidget(self._evaluation_selection_label, 0, 0)
        main_grid_layout.addWidget(self._evaluation_combo_box, 0, 1)

        main_grid_layout.addWidget(self._genote_update_label, 1, 0)
        main_grid_layout.addWidget(self._genote_update_button, 1, 1)

        main_grid_layout.addWidget(self._genote_update_file_path_label, 2, 1)

        main_grid_layout.addWidget(self._moodle_correction_label, 3, 0)
        main_grid_layout.addWidget(self._moodle_correction_archive_button, 3, 1)

        main_grid_layout.addWidget(self._moodle_correction_archive_path_label, 4, 1)

        main_grid_layout.setColumnStretch(0, 1)
        main_grid_layout.setColumnStretch(1, 3)

    @override
    def _connect_downstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._evaluation_combo_box.evaluationIDChanged,
                                    slot=self.evaluationIDChanged)
        nuitka_helpers.safe_connect(signal=self._moodle_correction_archive_button.clicked,
                                    slot=self.moodleArchiveButtonClicked)
        nuitka_helpers.safe_connect(signal=self._genote_update_button.clicked, slot=self.genoteUpdateButtonClicked)

    def populate_evaluation_id_combo_box(self, payload: ComboBoxPayload) -> None:
        self._evaluation_combo_box.populate_combo_box(payload=payload)

    def synchronized_evaluation_id(self, evaluation_id: int | None) -> None:
        self._evaluation_combo_box.synchronized_evaluation_id(evaluation_id=evaluation_id)

    def update_moodle_correction_path_label(self, label_text: MoodleCorrectionArchiveLabelText) -> None:
        self._moodle_correction_archive_path_label.setText(label_text.label_text)

    def update_genote_label(self, label_text: GeNoteLabelText) -> None:
        self._genote_update_file_path_label.setText(label_text.label_text)

    def update_genote_update_button_state(self, is_enabled: bool) -> None:
        self._genote_update_button.setEnabled(is_enabled)

    def update_moodle_archive_button_state(self, is_enabled: bool) -> None:
        self._moodle_correction_archive_button.setEnabled(is_enabled)

class GradeStatisticsGroupBox(QGroupBox, WidgetLifecycleMixin):
    _is_final_component = True

    launchStatsClicked = Signal()
    exportFiguresClicked = Signal()
    exportExcelClicked = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__("Statistiques de groupe pour les notes et les références valides et alignées avec le texte",
                         parent=parent)
        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self._launch_stats_button = QPushButton("Lancer la génération de statistiques ")
        self._reference_grade_figure = ReferenceGradePlotChart()
        self._export_figures_button = QPushButton("Exporter la figure")

        self._export_excel_button = QPushButton("Exporter le résultat dans Excel")
        self._export_excel_button.setVisible(False)

        self._reference_grade_figure.setVisible(False)
        self._export_figures_button.setVisible(False)

    def _assemble_layout(self) -> None:
        main_layout = QVBoxLayout(self)

        self._scroll_area = QScrollArea()
        self._scroll_area.setVisible(False)
        self._scroll_area.setMinimumHeight(700)
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded) # type: ignore[arg-type]
        self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # type: ignore[arg-type]

        container = QWidget()
        container.setMinimumHeight(700)
        container_layout = QVBoxLayout(container)

        container_layout.setAlignment(Qt.AlignmentFlag.AlignLeft) # type: ignore[arg-type]
        container_layout.addWidget(self._reference_grade_figure)

        self._scroll_area.setWidget(container)

        main_layout.addWidget(self._launch_stats_button, alignment=Qt.AlignmentFlag.AlignHCenter) # type: ignore[arg-type]
        main_layout.addSpacing(12)
        main_layout.addWidget(self._scroll_area)
        main_layout.addSpacing(24)
        main_layout.addWidget(self._export_figures_button)
        main_layout.addWidget(self._export_excel_button)

    def _connect_downstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._launch_stats_button.clicked, slot=self.launchStatsClicked)
        nuitka_helpers.safe_connect(signal=self._export_figures_button.clicked, slot=self.exportFiguresClicked)
        nuitka_helpers.safe_connect(signal=self._export_excel_button.clicked, slot=self.exportExcelClicked)

    @Slot(str)
    def set_charts_theme(self, theme_name: ThemeOptions) -> None:
        self._reference_grade_figure.set_theme(theme_name=theme_name)

    def update_figures_save_path(self, save_path: Path | str) -> None:
        self._reference_grade_figure.update_save_path(save_path=save_path)

    @Slot()
    def launch_stats_charts(self) -> None:
        self._reference_grade_figure.setVisible(True)
        self._export_figures_button.setVisible(True)
        self._scroll_area.setVisible(True)
        self._export_excel_button.setVisible(True)

    @Slot(GradeReferencePlotDTO)
    def load_reference_grade_plot_data(self, grade_reference_plot_dto: GradeReferencePlotDTO | None) -> None:
        self._reference_grade_figure.load_data(grade_reference_plot_dto=grade_reference_plot_dto)

    @Slot()
    def clear_charts(self) -> None:
        self._reference_grade_figure.figure.clf()
        self._reference_grade_figure.load_data(None)

        self._reference_grade_figure.setVisible(False)
        self._export_figures_button.setVisible(False)
        self._scroll_area.setVisible(False)
        self._export_excel_button.setVisible(False)

    @Slot(Path)
    def save_figures(self, save_path: Path | str) -> None:
        if save_path:
            self._reference_grade_figure.save_figure(save_path=str(save_path))
        else:
            self._reference_grade_figure.save_figure(save_path=None)