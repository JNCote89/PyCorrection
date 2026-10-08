from functools import partial
from pathlib import Path
from typing import override

from PySide6.QtCore import QTimer, Qt, Signal, Slot
from PySide6.QtWidgets import QApplication, QGroupBox, QHBoxLayout, QProgressBar, QPushButton, QVBoxLayout, QWidget

from src.py_correction.core import nuitka_helpers
from src.py_correction.core.domains.reference.reference_dtos import (ReferenceSubmissionsDTO, ReferenceTableDTO,
                                                                     ReferenceUpdateDTO)
from src.py_correction.core.domains.reference.reference_enums import RelevanceLevelEnum
from src.py_correction.core.domains.reference.reference_figures_dtos import (EvidenceLevelPieChartDTO,
                                                                             ReferenceTypeStackedBarChartDTO)
from src.py_correction.core.domains.shared.shared_dtos import ComboBoxPayload, WidgetItem
from src.py_correction.core.theme_manager import ThemeOptions
from src.py_correction.ui.components.base_components.widget_lifecycle_mixin import WidgetLifecycleMixin
from src.py_correction.ui.components.default_widgets.labels import (DefaultDynamicLabel, DefaultLabel,
                                                                    DefaultParagraphLabel)
from src.py_correction.ui.components.layouts import DefaultGridLayout
from src.py_correction.ui.components.shared_components.evaluation_selection.evaluation_selection_widgets import (
    EvaluationIDComboBox)
from src.py_correction.ui.components.shared_components.student_selection.student_selection_widget import (
    StudentIDComboBox)
from src.py_correction.ui.feedbacks.labels.directory_labels import (StudentEvaluationCorrectionLabelText,
                                                                    StudentEvaluationSubmissionLabelText)
from src.py_correction.ui.pages.reference.reference_widgets import (BibTextImportWidget, CollapsibleDeleteReferences,
                                                                    CollapsibleReferenceImportInstructions,
                                                                    ExcludeReferenceFilterGroup,
                                                                    ReferenceImportTextEdit,
                                                                    ReferenceTableModel, ReferenceTableView)
from src.py_correction.ui.pages.reference.reference_widgets import EvidenceLevelPieChart, ReferenceTypeStackedBarChart


class CorrectionManagementGroupBox(QGroupBox, WidgetLifecycleMixin):
    _is_final_component = True

    evaluationIDChanged = Signal(object)
    studentIDChanged = Signal(object)

    def __init__(self, parent: QWidget | None = None):
        super().__init__("Gestion de la correction", parent=parent)
        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self._evaluation_selection_label = DefaultLabel(
            text="Sélectionner une évaluation",
            alignment_h_flag=Qt.AlignmentFlag.AlignHCenter)  # type: ignore[arg-type]

        self._evaluation_combo_box = EvaluationIDComboBox()

        self._student_selection_label = DefaultLabel(text="Sélectionner un étudiant",
                                                     alignment_h_flag=Qt.AlignmentFlag.AlignHCenter) # type: ignore[arg-type]
        self._student_combo_box = StudentIDComboBox()

        self._evaluation_submission_directory_label = DefaultDynamicLabel(
            StudentEvaluationSubmissionLabelText().label_text)
        self._evaluation_correction_directory_label = DefaultDynamicLabel(
            StudentEvaluationCorrectionLabelText().label_text)

    @override
    def _assemble_layout(self) -> None:
        main_grid_layout = DefaultGridLayout(self)

        main_grid_layout.addWidget(self._evaluation_selection_label, 0, 0)
        main_grid_layout.addWidget(self._student_selection_label, 0, 1)

        main_grid_layout.addWidget(self._evaluation_combo_box, 1, 0)
        main_grid_layout.addWidget(self._student_combo_box, 1, 1)

        main_grid_layout.addWidget(self._evaluation_submission_directory_label, 2, 0, 1, 2)

        main_grid_layout.addWidget(self._evaluation_correction_directory_label, 3, 0, 1, 2)

    @override
    def _connect_downstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._evaluation_combo_box.evaluationIDChanged,
                                    slot=self.evaluationIDChanged)
        nuitka_helpers.safe_connect(signal=self._student_combo_box.studentIDChanged, slot=self.studentIDChanged)

    @Slot(ComboBoxPayload)
    def populate_evaluation_id_combo_box(self, payload: ComboBoxPayload) -> None:
        self._evaluation_combo_box.populate_combo_box(payload=payload)

    @Slot(ComboBoxPayload)
    def populate_student_id_combo_box(self, payload: ComboBoxPayload) -> None:
        self._student_combo_box.populate_combo_box(payload=payload)

    @Slot(int)
    def synchronized_evaluation_id(self, evaluation_id: int | None) -> None:
        self._evaluation_combo_box.synchronized_evaluation_id(evaluation_id=evaluation_id)

    @Slot(StudentEvaluationSubmissionLabelText)
    def update_evaluation_submission_directory_label(self, label_text: StudentEvaluationSubmissionLabelText) -> None:
        self._evaluation_submission_directory_label.setText(label_text.label_text)

    @Slot(StudentEvaluationCorrectionLabelText)
    def update_evaluation_correction_directory_label(self, label_text: StudentEvaluationCorrectionLabelText) -> None:
        self._evaluation_correction_directory_label.setText(label_text.label_text)


class ReferenceImportGroupBox(QGroupBox, WidgetLifecycleMixin):
    _is_final_component = True

    bibTextFilePathSubmitted = Signal(Path)
    referencesSubmitted = Signal(ReferenceSubmissionsDTO)

    def __init__(self, parent: QWidget | None = None):
        super().__init__("Importation des références", parent=parent)

        self._can_accept_new_import = True

        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self._bib_text_import_widget = BibTextImportWidget()

        self._import_instructions_label = CollapsibleReferenceImportInstructions()

        self._reference_verification_text = ReferenceImportTextEdit()

        self._exclude_reference_section = ExcludeReferenceFilterGroup()

        self._submit_references_button = QPushButton("Soumettre les références pour évaluation")
        self._table_view_delete_instructions_label = DefaultParagraphLabel(
            text=""" Pour recommencer l'importation, il faut supprimer les références évaluées dans la section
             "Références à évaluer" """, alignment_h_flag=Qt.AlignmentFlag.AlignHCenter) # type: ignore[arg-type]
        self._table_view_delete_instructions_label.setVisible(False)

    @override
    def _assemble_layout(self) -> None:
        main_layout = QVBoxLayout(self)

        main_layout.addWidget(self._bib_text_import_widget)
        main_layout.addWidget(self._import_instructions_label)
        main_layout.addWidget(self._reference_verification_text)
        main_layout.addWidget(self._exclude_reference_section)
        main_layout.addWidget(self._submit_references_button,
                              alignment=Qt.AlignmentFlag.AlignHCenter) # type: ignore[arg-type]
        main_layout.addWidget(self._table_view_delete_instructions_label) # type: ignore[arg-type]
        main_layout.addSpacing(24)
        main_layout.addStretch()

    @override
    def _connect_downstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._bib_text_import_widget.bibTextFilePathSubmitted,
                                    slot=self.bibTextFilePathSubmitted)
        nuitka_helpers.safe_connect(signal=self._submit_references_button.clicked,
                                    slot=self._on_references_submit)

    @override
    def _connect_internal_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._reference_verification_text.textChanged,
                                    slot=self._refresh_submit_button_state)

    def import_bib_text_inside_edit_line(self, text: str) -> None:
        self._reference_verification_text.setPlainText(text)

    def update_reference_verification_group_box_title(self, citation_style: str) -> None:
        self.setTitle(f"Importation des références ({citation_style})")

    @Slot(list)
    def update_evaluation_filter_list(self, widget_items: list[WidgetItem]) -> None:
        self._exclude_reference_section.update_evaluation_filter_list(widget_items=widget_items)

    @Slot(bool)
    def table_view_empty_state(self, is_empty: bool) -> None:
        """To avoid resubmitting references if the reference table view is populated."""
        self._can_accept_new_import = is_empty

        self._table_view_delete_instructions_label.setVisible(not bool(is_empty))

        self._refresh_submit_button_state()

    @Slot()
    def _on_references_submit(self) -> None:
        references = self._reference_verification_text.get_references()
        excluded_evaluation_ids = self._exclude_reference_section.get_evaluation_filter_list()

        references_submission = ReferenceSubmissionsDTO(references=references,
                                                        excluded_evaluation_ids=excluded_evaluation_ids)
        self.referencesSubmitted.emit(references_submission)

        self._reference_verification_text.clear()

    @Slot()
    def _refresh_submit_button_state(self) -> None:
        import_widget_has_text = bool(self._reference_verification_text.toPlainText().strip())
        button_state = import_widget_has_text and self._can_accept_new_import

        self._submit_references_button.setEnabled(button_state)


class ReferenceTableViewGroupbox(QGroupBox, WidgetLifecycleMixin):
    _is_final_component = True

    referenceUpdated = Signal(ReferenceUpdateDTO)

    isEmptyStatusChanged = Signal(bool)

    referenceDeletedButtonClicked = Signal()
    automaticVerificationButtonClicked = Signal()
    abortVerificationClicked = Signal()
    excelExportClicked = Signal()
    batchRelevanceRelevantClicked = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__("Références à évaluer", parent=parent)
        self._is_table_empty = True

        self._init_ui()

        self._delay_timer = QTimer(self)
        self._delay_timer.setSingleShot(True)
        self._delay_timer.setInterval(500)
        self._timer_is_connected = False

    @override
    def _create_widgets(self) -> None:
        self._delete_collapsible_section = CollapsibleDeleteReferences()

        self._automatic_verification_button = QPushButton("Lancer la vérification automatique des références")

        self._progress_bar = QProgressBar()
        self._abort_verification_button = QPushButton("Arrêter la vérification automatique")
        self._progress_bar.setVisible(False)
        self._abort_verification_button.setVisible(False)

        self._reference_table_model = ReferenceTableModel()
        self._reference_table_view = ReferenceTableView(table_model=self._reference_table_model)

        self._batch_relevance_evaluation_label = DefaultLabel(text="Évaluation en lot de la pertinence et de "
                                                                   "l'alignement avec le texte",
                                                              subtext="Modifie seulement les références non évaluées")
        self._batch_relevance_evaluation_button = QPushButton(f'Insérer la valeur "{RelevanceLevelEnum.RELEVANT}"')

        self._excel_export_button = QPushButton("Exporter le résultat dans Excel")
        self._excel_export_button.setVisible(False)

    @override
    def _assemble_layout(self) -> None:
        self._batch_evaluation_container = QWidget()
        self._batch_evaluation_container.setVisible(False)
        batch_evaluation_layout = QHBoxLayout(self._batch_evaluation_container)
        batch_evaluation_layout.addWidget(self._batch_relevance_evaluation_label, 1)
        batch_evaluation_layout.addWidget(self._batch_relevance_evaluation_button, 3)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self._delete_collapsible_section)
        self.main_layout.addWidget(self._automatic_verification_button,
                                   alignment=Qt.AlignmentFlag.AlignHCenter) # type: ignore[arg-type]
        self.main_layout.addWidget(self._progress_bar)
        self.main_layout.addWidget(self._abort_verification_button,
                                   alignment=Qt.AlignmentFlag.AlignHCenter) # type: ignore[arg-type]
        self.main_layout.addSpacing(12)
        self.main_layout.addWidget(self._reference_table_view)
        self.main_layout.addSpacing(12)
        self.main_layout.addWidget(self._batch_evaluation_container)
        self.main_layout.addSpacing(12)
        self.main_layout.addWidget(self._excel_export_button)
        self.main_layout.addStretch()

    @override
    def _connect_downstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._reference_table_model.referenceUpdated, slot=self.referenceUpdated)
        nuitka_helpers.safe_connect(signal=self._delete_collapsible_section.referenceDeletedButtonClicked,
                                    slot=self.referenceDeletedButtonClicked)
        nuitka_helpers.safe_connect(signal=self._automatic_verification_button.clicked,
                                    slot=self.automaticVerificationButtonClicked)
        nuitka_helpers.safe_connect(signal=self._abort_verification_button.clicked, slot=self.abortVerificationClicked)
        nuitka_helpers.safe_connect(signal=self._excel_export_button.clicked, slot=self.excelExportClicked)
        nuitka_helpers.safe_connect(signal=self._batch_relevance_evaluation_button.clicked,
                                    slot=self.batchRelevanceRelevantClicked)

    @Slot(ReferenceTableDTO)
    def set_references(self, references: list[ReferenceTableDTO] | None) -> None:
        if not references:
            references = []
            self._excel_export_button.setVisible(False)
            self._batch_evaluation_container.setVisible(False)
        else:
            self._excel_export_button.setVisible(True)
            self._batch_evaluation_container.setVisible(True)

        self._reference_table_model.set_references(reference_table_dtos=references)

        # To remove the scrolling bar which duplicate the scrolling area with the page, making navigation difficult.
        self._reference_table_view.adjust_table_height()

        self._is_table_empty = not bool(references)
        self._automatic_verification_button.setEnabled(not self._is_table_empty)
        self.isEmptyStatusChanged.emit(self._is_table_empty)

    @Slot(ReferenceTableDTO)
    def update_row(self, reference_dto: ReferenceTableDTO) -> None:
        if reference_dto:
            self._reference_table_model.update_row(reference_table_dto=reference_dto)

            QApplication.processEvents()
            self._reference_table_view.resizeRowsToContents()
            QTimer.singleShot(0, self._reference_table_view.adjust_table_height)

    @Slot(int)
    def set_progress_bar_started(self, maximum_range: int) -> None:
        self._automatic_verification_button.setEnabled(False)
        self._excel_export_button.setEnabled(False)

        if self._timer_is_connected:
            self._delay_timer.timeout.disconnect()
            self._timer_is_connected = False

        nuitka_helpers.safe_connect(signal=self._delay_timer.timeout,
                                    slot=partial(self._show_progress_bar, maximum_range))
        self._delay_timer.start()
        self._timer_is_connected = True

    @Slot(int)
    def update_progress_bar_value(self, value: int) -> None:
        self._progress_bar.setValue(value)

    @Slot(bool)
    def set_progress_bar_finished(self) -> None:
        if self._delay_timer.isActive():
            self._delay_timer.stop()
            self._timer_is_connected = False

        self._progress_bar.setVisible(False)
        self._abort_verification_button.setVisible(False)
        self._automatic_verification_button.setEnabled(True)
        self._excel_export_button.setEnabled(True)
        self._excel_export_button.setVisible(True)
        self._batch_evaluation_container.setVisible(True)
        self._progress_bar.reset()

    def _show_progress_bar(self, maximum_range: int) -> None:
        self._progress_bar.setRange(1, maximum_range)
        self._progress_bar.setVisible(True)
        self._abort_verification_button.setVisible(True)


class ReferenceStatisticsGroupBox(QGroupBox, WidgetLifecycleMixin):
    _is_final_component = True

    launchStatsClicked = Signal()
    exportFiguresClicked = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__("Statistiques des références valides et alignées avec le texte", parent=parent)
        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self._launch_stats_button = QPushButton("Lancer la génération de statistiques ")
        self._reference_type_figure = ReferenceTypeStackedBarChart()
        self._evidence_level_figure = EvidenceLevelPieChart()
        self._export_figures_button = QPushButton("Exporter les figures")

        self._reference_type_figure.setVisible(False)
        self._evidence_level_figure.setVisible(False)
        self._export_figures_button.setVisible(False)

    def _assemble_layout(self) -> None:
        main_layout = QVBoxLayout(self)

        main_layout.addWidget(self._launch_stats_button,
                              alignment=Qt.AlignmentFlag.AlignHCenter) # type: ignore[arg-type]
        main_layout.addSpacing(12)
        main_layout.addWidget(self._reference_type_figure)
        main_layout.addSpacing(12)
        main_layout.addWidget(self._evidence_level_figure)
        main_layout.addSpacing(12)
        main_layout.addWidget(self._export_figures_button)

    def _connect_downstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._launch_stats_button.clicked, slot=self.launchStatsClicked)
        nuitka_helpers.safe_connect(signal=self._export_figures_button.clicked, slot=self.exportFiguresClicked)

    @Slot(str)
    def set_charts_theme(self, theme_name: ThemeOptions) -> None:
        self._evidence_level_figure.set_theme(theme_name=theme_name)
        self._reference_type_figure.set_theme(theme_name=theme_name)

    def update_figures_save_path(self, save_path: Path) -> None:
        self._evidence_level_figure.update_save_path(save_path=save_path)
        self._reference_type_figure.update_save_path(save_path=save_path)

    @Slot()
    def launch_stats_charts(self) -> None:
        self._reference_type_figure.setVisible(True)
        self._evidence_level_figure.setVisible(True)
        self._export_figures_button.setVisible(True)

    @Slot(EvidenceLevelPieChartDTO)
    def load_pie_chart_data(self, pie_chart_dto: EvidenceLevelPieChartDTO) -> None:
        self._evidence_level_figure.load_data(pie_chart_dto=pie_chart_dto)

    @Slot(ReferenceTypeStackedBarChartDTO)
    def load_bar_chart_data(self, bar_chart_dto: ReferenceTypeStackedBarChartDTO) -> None:
        self._reference_type_figure.load_data(reference_type_stacked_bar_chart_dto=bar_chart_dto)

    @Slot()
    def clear_charts(self) -> None:
        self._evidence_level_figure.figure.clf()
        self._evidence_level_figure.load_data(None)

        self._reference_type_figure.figure.clf()
        self._reference_type_figure.load_data(None)

        self._reference_type_figure.setVisible(False)
        self._evidence_level_figure.setVisible(False)
        self._export_figures_button.setVisible(False)

    @Slot(Path)
    def save_figures(self, save_path: Path | None) -> None:
        if save_path:
            self._reference_type_figure.save_figure(save_path=f"{save_path} - type_de_références.png")
            self._evidence_level_figure.save_figure(save_path=f"{save_path} - niveau_de_preuves.png")
        else:
            self._reference_type_figure.save_figure(save_path=None)
            self._evidence_level_figure.save_figure(save_path=None)

    @Slot(bool)
    def table_view_empty_state(self, is_empty: bool) -> None:
        """To avoid resubmitting references if the reference table view is populated."""
        self._launch_stats_button.setEnabled(not bool(is_empty))