from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, override

from PySide6.QtCore import QTimer, Qt, Signal, Slot
from PySide6.QtWidgets import QApplication, QFileDialog, QWidget

from src.py_correction.core import nuitka_helpers
from src.py_correction.core.dependency_injection import container
from src.py_correction.core.domains.reference.reference_dtos import (DryRunWarningResponseDTO, ReferenceSubmissionsDTO,
                                                                     ReferenceTableDTO)
from src.py_correction.core.domains.reference.reference_dtos import ReferenceUpdateDTO
from src.py_correction.core.domains.reference.reference_figures_dtos import (EvidenceLevelPieChartDTO,
                                                                             ReferenceTypeStackedBarChartDTO)
from src.py_correction.core.domains.shared.shared_dtos import WidgetItem
from src.py_correction.engine.reference.parsers.bibtext_parser import render_bibliography
from src.py_correction.ui.components.base_components.base_controller import BaseController
from src.py_correction.ui.components.payload_builders import evaluation_payloads, settings_payloads, student_payloads
from src.py_correction.ui.components.shared_components.course_selection.course_selection_controller import (
    CourseSelectionController)
from src.py_correction.ui.components.shared_components.workflow.workflow_mixin import ResetWorkflowMixin
from src.py_correction.ui.feedbacks.labels.directory_labels import (StudentEvaluationCorrectionLabelText,
                                                                    StudentEvaluationSubmissionLabelText)
from src.py_correction.ui.pages.reference.reference_workers import ReferenceVerificationWorker

if TYPE_CHECKING:
    from src.py_correction.ui.pages.reference.reference_sections import (CorrectionManagementGroupBox,
                                                                     ReferenceStatisticsGroupBox,
                                                                     ReferenceImportGroupBox,
                                                                     ReferenceTableViewGroupbox)
    from src.py_correction.ui.pages.reference.reference_page import ReferencePage


@dataclass
class ReferenceTransactionWorkflow(ResetWorkflowMixin):
    course_id: int | None = None
    evaluation_id: int | None = None
    student_id: int | None = None

    evaluation_submission_directories: list[Path] | None = None
    evaluation_correction_directory: Path | None = None

    imported_references: list[ReferenceTableDTO] | None = field(default_factory=list)


class CorrectionManagementController(BaseController):

    def __init__(self, section_view: "CorrectionManagementGroupBox", workflow: ReferenceTransactionWorkflow,
                 parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._workflow = workflow
        self._section_view = section_view

        self._settings_manager = container.settings_manager()
        self._student_services = container.student_services()
        self._course_services = container.course_services()
        self._course_student_services = container.course_student_services()
        self._evaluation_services = container.evaluation_services()
        self._reference_orchestrator = container.reference_orchestrator()

        self._event_bus = container.event_bus()

        self._init_controller()

        self._processing_label_update = False

    @override
    def _connect_upstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._event_bus.student.dataChanged, slot=self._refresh_student_id_combo_box)
        nuitka_helpers.safe_connect(signal=self._event_bus.evaluation.dataChanged,
                                    slot=self._refresh_evaluation_id_combo_box)

        nuitka_helpers.safe_connect(signal=self._event_bus.submission.correctionFileUpdated,
                                    slot=self._update_evaluation_correction_directory_label)
        nuitka_helpers.safe_connect(signal=self._event_bus.submission.submissionFileUpdated,
                                    slot=self._update_evaluation_submission_directory_label)

    @override
    def _connect_downstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._section_view.evaluationIDChanged,
                                    slot=self._event_bus.selection_widget.evaluationIDChanged)
        nuitka_helpers.safe_connect(signal=self._section_view.studentIDChanged,
                                    slot=self._event_bus.selection_widget.studentIDChanged)

    def update_selection_widgets(self) -> None:
        if self._workflow.course_id is not None:
            self._refresh_evaluation_id_combo_box()
            self._refresh_student_id_combo_box()

    def synchronized_evaluation_id(self, evaluation_id: int | None) -> None:
        self._section_view.synchronized_evaluation_id(evaluation_id=evaluation_id)

    def schedule_directory_labels_update(self) -> None:
        if not self._processing_label_update:
            self._processing_label_update = True

            QTimer.singleShot(0, self._perform_labels_update)

    @Slot()
    def _refresh_student_id_combo_box(self) -> None:
        if self._workflow.course_id:
            student_records = self._course_student_services.list_active_student_records(
                course_id=self._workflow.course_id)

            combo_box_payload = student_payloads.get_student_id_combo_box_payload(
                current_data_selection=self._settings_manager.restored_settings.student_id_selected,
                student_selection_dtos=student_records)
            self._section_view.populate_student_id_combo_box(payload=combo_box_payload)

    @Slot()
    def _refresh_evaluation_id_combo_box(self) -> None:
        if self._workflow.course_id:
            evaluation_selection_dtos = self._evaluation_services.list_evaluation_selection_dtos(
                course_id=self._workflow.course_id)

            combo_box_payload = evaluation_payloads.get_evaluation_id_combo_box_payload(
                current_data_selection=self._settings_manager.restored_settings.evaluation_id_selected,
                evaluation_selection_dtos=evaluation_selection_dtos)
            self._section_view.populate_evaluation_id_combo_box(payload=combo_box_payload)

    @Slot()
    def _update_evaluation_submission_directory_label(self):
        if (self._workflow.course_id is not None
                and self._workflow.evaluation_id is not None
                and self._workflow.student_id is not None):

            evaluation_submission_directory = self._reference_orchestrator.get_evaluation_submission_directory(
                course_id=self._workflow.course_id,
                evaluation_id=self._workflow.evaluation_id,
                student_id=self._workflow.student_id)

            if self._workflow.evaluation_submission_directories != evaluation_submission_directory:
                self._workflow.evaluation_submission_directories = evaluation_submission_directory

        evaluation_submission_directory_label_text = StudentEvaluationSubmissionLabelText(
            directories=self._workflow.evaluation_submission_directories)
        self._section_view.update_evaluation_submission_directory_label(
            label_text=evaluation_submission_directory_label_text)

    @Slot()
    def _update_evaluation_correction_directory_label(self) -> None:
        if (self._workflow.course_id is not None and self._workflow.evaluation_id is not None
            and self._workflow.student_id is not None):

            evaluation_correction_directory = self._reference_orchestrator.get_evaluation_correction_directory(
                course_id=self._workflow.course_id,
                evaluation_id=self._workflow.evaluation_id,
                student_id=self._workflow.student_id)

            if self._workflow.evaluation_correction_directory != evaluation_correction_directory:
                self._workflow.evaluation_correction_directory = evaluation_correction_directory

        evaluation_correction_directory_label_text = StudentEvaluationCorrectionLabelText(
            directory=self._workflow.evaluation_correction_directory)
        self._section_view.update_evaluation_correction_directory_label(
            label_text=evaluation_correction_directory_label_text)

    def _perform_labels_update(self):
        if not self._processing_label_update:
            return

        self._processing_label_update = False

        self._update_evaluation_correction_directory_label()
        self._update_evaluation_submission_directory_label()


class ReferenceImportController(BaseController):
    referenceImported = Signal()

    def __init__(self, section_view: "ReferenceImportGroupBox", workflow: ReferenceTransactionWorkflow,
                 parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._workflow = workflow
        self._section_view = section_view

        self._settings_manager = container.settings_manager()
        self._course_services = container.course_services()
        self._reference_orchestrator = container.reference_orchestrator()

        self._event_bus = container.event_bus()

        self._init_controller()

        self._processing_filter_list_update = False

    @override
    def _connect_upstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._event_bus.evaluation.dataChanged,
                                    slot=self.schedule_evaluation_filter_list_update)

    @override
    def _connect_downstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._section_view.bibTextFilePathSubmitted,
                                    slot=self._handle_bib_text_imported)
        nuitka_helpers.safe_connect(signal=self._section_view.referencesSubmitted,
                                    slot=self._handle_references_submitted)

    @override
    def _refresh_view(self):
        self._refresh_citation_style()

    @Slot()
    def schedule_evaluation_filter_list_update(self) -> None:
        if not self._processing_filter_list_update:
            self._processing_filter_list_update = True

            QTimer.singleShot(0, self._perform_evaluation_filter_list_update)

    @Slot(Path)
    def _handle_bib_text_imported(self, file_path: Path) -> None:
        with QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor): # type: ignore[arg-type]
            output_text = render_bibliography(bib_path=file_path)
            self._section_view.import_bib_text_inside_edit_line(text=output_text)

    @Slot(ReferenceSubmissionsDTO)
    def _handle_references_submitted(self, reference_submissions_dto: ReferenceSubmissionsDTO) -> None:
        if reference_submissions_dto:

            if (self._workflow.course_id is None or self._workflow.evaluation_id is None
                    or self._workflow.student_id is None):
                warning_dto = DryRunWarningResponseDTO(course_id=self._workflow.course_id,
                                                       evaluation_id=self._workflow.evaluation_id,
                                                       student_id=self._workflow.student_id)
                self._event_bus.reference.dryRunWarningEmitted.emit(warning_dto)

            with QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor): # type: ignore[arg-type]

                response_dtos = self._reference_orchestrator.save_and_get_reference_table_dtos(
                    evaluation_id=self._workflow.evaluation_id,
                    student_id=self._workflow.student_id, reference_submissions_dto=reference_submissions_dto)

                self._workflow.imported_references = response_dtos
                self.referenceImported.emit()

    def _perform_evaluation_filter_list_update(self):
        if not self._processing_filter_list_update:
            return

        self._processing_filter_list_update = False

        if self._workflow.course_id is not None:
            course_evaluations = self._course_services.get_course_evaluations(
                course_id=self._workflow.course_id)
            if course_evaluations:
                widget_items = [WidgetItem(label=evaluation.title, internal_value=evaluation.id)
                                for evaluation in course_evaluations
                                if evaluation.id != self._workflow.evaluation_id]

                self._section_view.update_evaluation_filter_list(widget_items=widget_items)

    def _refresh_citation_style(self):
        restored_citation_style = settings_payloads.get_citation_style_label(
            self._settings_manager.restored_settings.citation_style)
        self._section_view.update_reference_verification_group_box_title(restored_citation_style)


class ReferenceTableViewController(BaseController):
    referencesDeleted = Signal()

    def __init__(self, section_view: "ReferenceTableViewGroupbox", workflow: ReferenceTransactionWorkflow,
                 parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._workflow = workflow
        self._section_view = section_view

        self._current_worker = None
        self._worker_registry = container.worker_registry()
        self._reference_services = container.reference_services()
        self._student_evaluation_services = container.student_evaluation_services()
        self._reference_orchestrator = container.reference_orchestrator()

        self._event_bus = container.event_bus()

        self._init_controller()

        self._processing_reference_table_update = False

    @override
    def _connect_downstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._section_view.referenceDeletedButtonClicked,
                                    slot=self._handle_delete_reference_button_clicked)
        nuitka_helpers.safe_connect(signal=self._section_view.automaticVerificationButtonClicked,
                                    slot=self._handle_automatic_verification_clicked)
        nuitka_helpers.safe_connect(signal=self._section_view.referenceUpdated, slot=self._handle_table_update)
        nuitka_helpers.safe_connect(signal=self._section_view.abortVerificationClicked, slot=self._abort_verification)
        nuitka_helpers.safe_connect(signal=self._section_view.excelExportClicked, slot=self._export_table_to_excel)
        nuitka_helpers.safe_connect(signal=self._section_view.batchRelevanceRelevantClicked,
                                    slot=self._modify_relevance_relevant_value)

    def schedule_reference_table_view_update(self) -> None:
        if not self._processing_reference_table_update:
            self._processing_reference_table_update = True

            QTimer.singleShot(0, self._perform_reference_table_update)

    @Slot()
    def _handle_automatic_verification_clicked(self) -> None:
        if self._workflow.evaluation_id is not None and self._workflow.student_id is not None:
            reference_table_dtos = self._reference_orchestrator.get_reference_table_dtos(
                evaluation_id=self._workflow.evaluation_id, student_id=self._workflow.student_id)

            self._run_verification(reference_table_dtos=reference_table_dtos,
                                   verification_function=self._reference_orchestrator.reference_verification)

        elif self._workflow.imported_references:

            self._run_verification(reference_table_dtos=self._workflow.imported_references,
                                   verification_function=self._reference_orchestrator.dry_reference_verification)

    @Slot()
    def _abort_verification(self) -> None:
        if self._current_worker is not None:
            self._current_worker.requestInterruption()
            self._current_worker = None

    @Slot()
    def _handle_table_update(self, update_dto: ReferenceUpdateDTO) -> None:
        self._reference_services.update_reference(reference_update_dto=update_dto)

    @Slot()
    def _handle_delete_reference_button_clicked(self) -> None:
        self._reference_orchestrator.delete_references(evaluation_id=self._workflow.evaluation_id,
                                                       student_id=self._workflow.student_id)
        self._workflow.imported_references = None
        self.referencesDeleted.emit()
        self.schedule_reference_table_view_update()

    @Slot()
    def _modify_relevance_relevant_value(self) -> None:
        with QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor): # type: ignore[arg-type]

            if self._workflow.evaluation_id is not None and self._workflow.student_id is not None:
                table_dtos = self._student_evaluation_services.get_reference_table_dtos(
                    student_id=self._workflow.student_id, evaluation_id=self._workflow.evaluation_id)

                if table_dtos:
                    modify_dtos = self._reference_orchestrator.batch_relevant_evaluation(
                        reference_table_dtos=table_dtos)
                    self._section_view.set_references(modify_dtos)

            elif self._workflow.imported_references:
                for reference in self._workflow.imported_references:
                    modify_dto = self._reference_orchestrator.dry_batch_relevant_evaluation(
                        reference_table_dto=reference)
                    self._section_view.update_row(modify_dto)

    @Slot()
    def _restore_cursor(self) -> None:
        QApplication.restoreOverrideCursor()

    @Slot()
    def _export_table_to_excel(self) -> None:
        if self._workflow.evaluation_id is not None and self._workflow.student_id is not None:
            dto_to_export = self._student_evaluation_services.get_reference_table_dtos(
                student_id=self._workflow.student_id, evaluation_id=self._workflow.evaluation_id)
        else:
            dto_to_export = self._workflow.imported_references

        if dto_to_export:
            saving_directory = self._reference_orchestrator.get_save_path(
                course_id=self._workflow.course_id, evaluation_id=self._workflow.evaluation_id,
                student_id=self._workflow.student_id)

            export_path, _ = QFileDialog.getSaveFileName(self, "Sauvegarder la figure",
                                                         f"{saving_directory} - références_évaluées.xlsx",
                                                         "Excel Files (*.xlsx)")
            if export_path:
                self._reference_services.export_table_to_excel(reference_table_dtos=dto_to_export,
                                                               export_path=export_path)

    def _run_verification(self, reference_table_dtos: list[ReferenceTableDTO],
                          verification_function: Callable[[ReferenceTableDTO], ReferenceTableDTO]) -> None:
        QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor) # type: ignore[arg-type]

        # Very important to provide the self parent argument to avoid premature garbage collection on Python side!
        self._current_worker = ReferenceVerificationWorker(verification_function=verification_function,
                                                           reference_table_dtos=reference_table_dtos,
                                                           parent=self)

        nuitka_helpers.safe_connect(signal=self._current_worker.progressBarStarted,
                                    slot=self._section_view.set_progress_bar_started)
        nuitka_helpers.safe_connect(signal=self._current_worker.progressBarUpdated,
                                    slot=self._section_view.update_progress_bar_value)
        nuitka_helpers.safe_connect(signal=self._current_worker.progressBarFinished,
                                    slot=self._section_view.set_progress_bar_finished)
        nuitka_helpers.safe_connect(signal=self._current_worker.rowUpdated,
                                    slot=self._section_view.update_row)

        # For clean garbage collection
        nuitka_helpers.safe_connect(signal=self._current_worker.finished,
                                    slot=self._current_worker.deleteLater)
        nuitka_helpers.safe_connect(signal=self._current_worker.finished,
                                    slot=self._restore_cursor)

        self._worker_registry.register(name="reference_verification_worker", worker=self._current_worker)

        self._current_worker.start()

    def _perform_reference_table_update(self):
        if not self._processing_reference_table_update:
            return

        self._processing_reference_table_update = False

        if self._workflow.evaluation_id is not None and self._workflow.student_id is not None:
            reference_table_dtos = self._student_evaluation_services.get_reference_table_dtos(
                student_id=self._workflow.student_id, evaluation_id=self._workflow.evaluation_id)
            self._section_view.set_references(references=reference_table_dtos)
        else:
            self._section_view.set_references(references=self._workflow.imported_references)


class ReferenceStatisticsController(BaseController):

    def __init__(self, section_view: "ReferenceStatisticsGroupBox", workflow: ReferenceTransactionWorkflow,
                 parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._workflow = workflow
        self._section_view = section_view

        self._settings_manager = container.settings_manager()
        self._reference_services = container.reference_services()
        self._student_evaluation_services = container.student_evaluation_services()
        self._reference_orchestrator = container.reference_orchestrator()

        self._event_bus = container.event_bus()

        self._init_controller()

        self._figure_dtos_loaded = False

    @override
    def _connect_upstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._event_bus.settings.uiThemeChanged,
                                    slot=self._section_view.set_charts_theme)
        nuitka_helpers.safe_connect(signal=self._event_bus.settings.userRootDirectoryChanged,
                                    slot=self._section_view.update_figures_save_path)

        nuitka_helpers.safe_connect(signal=self._event_bus.selection_widget.studentIDChanged, slot=self.clear_charts)

    @override
    def _connect_downstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._section_view.launchStatsClicked, slot=self._launch_stats_generation)
        nuitka_helpers.safe_connect(signal=self._section_view.exportFiguresClicked, slot=self._save_figures)

    @override
    def _refresh_view(self) -> None:
        self._refresh_chart_theme()
        self._refresh_save_directory()

    def clear_charts(self) -> None:
        if self._figure_dtos_loaded:
            self._section_view.clear_charts()
            self._figure_dtos_loaded = False

    @Slot()
    def _launch_stats_generation(self) -> None:
        pie_chart_dto: EvidenceLevelPieChartDTO | None = None
        bar_chart_dto: ReferenceTypeStackedBarChartDTO | None = None

        with QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor): # type: ignore[arg-type]

            if self._workflow.evaluation_id is not None and self._workflow.student_id is not None:
                reference_table_dtos = self._reference_orchestrator.get_reference_table_dtos(
                    evaluation_id=self._workflow.evaluation_id, student_id=self._workflow.student_id)

                if reference_table_dtos:
                    pie_chart_dto = self._reference_services.get_evidence_level_pie_chart_dto(
                        reference_table_dtos=reference_table_dtos)
                    bar_chart_dto = self._reference_services.get_reference_type_stacked_bar_chart_dto(
                        reference_table_dtos=reference_table_dtos)

            elif self._workflow.imported_references:
                pie_chart_dto = self._reference_services.get_evidence_level_pie_chart_dto(
                    reference_table_dtos=self._workflow.imported_references)

                bar_chart_dto = self._reference_services.get_reference_type_stacked_bar_chart_dto(
                    reference_table_dtos=self._workflow.imported_references)

            if pie_chart_dto:
                self._section_view.load_pie_chart_data(pie_chart_dto=pie_chart_dto)

            if bar_chart_dto:
                self._section_view.load_bar_chart_data(bar_chart_dto=bar_chart_dto)

        self._figure_dtos_loaded = True
        self._section_view.launch_stats_charts()

    @Slot()
    def _save_figures(self) -> None:
        save_path = self._reference_orchestrator.get_save_path(course_id=self._workflow.course_id,
                                                               evaluation_id=self._workflow.evaluation_id,
                                                               student_id=self._workflow.student_id)
        self._section_view.save_figures(save_path)

    def _refresh_chart_theme(self) -> None:
        current_ui_theme = self._settings_manager.restored_settings.ui_theme
        self._section_view.set_charts_theme(current_ui_theme)

    def _refresh_save_directory(self) -> None:
        user_root_directory = self._settings_manager.restored_settings.user_root_directory
        self._section_view.update_figures_save_path(user_root_directory)


class ReferencePageController(BaseController):

    def __init__(self, page_view: "ReferencePage", parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._page_view = page_view

        self._workflow = ReferenceTransactionWorkflow()

        self._course_selection_controller = CourseSelectionController(
            course_selection_group_box_view=self._page_view.course_selection_group_box)

        self._correction_management_controller = CorrectionManagementController(
            workflow=self._workflow, section_view=self._page_view.correction_management_group_box)
        self._reference_import_controller = ReferenceImportController(
            workflow=self._workflow, section_view=self._page_view.reference_import_group_box)
        self._reference_table_view_controller = ReferenceTableViewController(
            workflow=self._workflow, section_view=self._page_view.reference_table_view_group_box)
        self._reference_statistics_controller = ReferenceStatisticsController(
            workflow=self._workflow, section_view=self._page_view.reference_statistics_group_box)

        self._course_services = container.course_services()

        self._event_bus = container.event_bus()

        self._init_controller()

    @override
    def _connect_internal_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._page_view.reference_table_view_group_box.isEmptyStatusChanged,
                                    slot=self._page_view.reference_import_group_box.table_view_empty_state)
        nuitka_helpers.safe_connect(signal=self._page_view.reference_table_view_group_box.isEmptyStatusChanged,
                                    slot=self._page_view.reference_statistics_group_box.table_view_empty_state)

        nuitka_helpers.safe_connect(signal=self._reference_import_controller.referenceImported,
                                    slot=self._reference_table_view_controller.schedule_reference_table_view_update)

        nuitka_helpers.safe_connect(signal=self._reference_table_view_controller.referencesDeleted,
                                    slot=self._reference_statistics_controller.clear_charts)

    @override
    def _connect_upstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._event_bus.selection_widget.courseIDChanged,
                                    slot=self._handle_course_id_changed)
        nuitka_helpers.safe_connect(signal=self._event_bus.selection_widget.evaluationIDChanged,
                                    slot=self._handle_evaluation_id_changed)
        nuitka_helpers.safe_connect(signal=self._event_bus.selection_widget.studentIDChanged,
                                    slot=self._handle_student_id_changed)

        nuitka_helpers.safe_connect(signal=self._event_bus.course.dataChanged, slot=self._refresh_view)
        nuitka_helpers.safe_connect(signal=self._event_bus.database.courseHasValidData, slot=self._toggle_ui_state)

    @Slot()
    @override
    def _refresh_view(self) -> None:
        self._course_selection_controller.refresh_combo_box_selection()
        self._course_services.check_valid_data()

    @Slot(object)
    def _handle_course_id_changed(self, course_id: int | None) -> None:
        if self._workflow.course_id != course_id:
            self._workflow.reset_workflow()

            self._workflow.course_id = course_id

            self._correction_management_controller.update_selection_widgets()

            self._reference_import_controller.schedule_evaluation_filter_list_update()
            self._correction_management_controller.schedule_directory_labels_update()
            self._reference_table_view_controller.schedule_reference_table_view_update()
            self._reference_statistics_controller.clear_charts()

    @Slot(object)
    def _handle_evaluation_id_changed(self, evaluation_id: int | None) -> None:
        if evaluation_id != self._workflow.evaluation_id:
            self._workflow.evaluation_id = evaluation_id

            self._correction_management_controller.synchronized_evaluation_id(evaluation_id=evaluation_id)

            self._reference_import_controller.schedule_evaluation_filter_list_update()
            self._correction_management_controller.schedule_directory_labels_update()
            self._reference_table_view_controller.schedule_reference_table_view_update()
            self._reference_statistics_controller.clear_charts()

    @Slot(object)
    def _handle_student_id_changed(self, student_id: int | None) -> None:
        if student_id != self._workflow.student_id:
            self._workflow.student_id = student_id

            self._correction_management_controller.schedule_directory_labels_update()
            self._reference_table_view_controller.schedule_reference_table_view_update()
            self._reference_statistics_controller.clear_charts()

    @Slot(bool)
    def _toggle_ui_state(self, course_has_valid_data: bool) -> None:
        self._page_view.set_ui_state(enabled_page_widgets=course_has_valid_data)

