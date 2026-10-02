from dataclasses import dataclass
from typing import TYPE_CHECKING, override

from PySide6.QtCore import QTimer, Qt, Slot
from PySide6.QtWidgets import QApplication, QFileDialog, QWidget

from src.py_correction.core import nuitka_helpers
from src.py_correction.core.dependency_injection import container
from src.py_correction.ui.components.base_components.base_controller import BaseController
from src.py_correction.ui.components.payload_builders import evaluation_payloads
from src.py_correction.ui.components.shared_components.course_selection.course_selection_controller import (
    CourseSelectionController)
from src.py_correction.ui.components.shared_components.workflow.workflow_mixin import ResetWorkflowMixin
from src.py_correction.ui.feedbacks.labels.directory_labels import (GeNoteLabelText, MoodleCorrectionArchiveLabelText)

if TYPE_CHECKING:
    from src.py_correction.ui.pages.grade.grade_page import GradePage
    from src.py_correction.ui.pages.grade.grade_sections import GradeManagementGroupBox, GradeStatisticsGroupBox


@dataclass
class GradeTransactionWorkflow(ResetWorkflowMixin):
    course_id: int | None = None
    evaluation_id: int | None = None


class GradeManagementController(BaseController):

    def __init__(self, section_view: "GradeManagementGroupBox", workflow: GradeTransactionWorkflow,
                 parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._section_view = section_view
        self._workflow = workflow

        self._settings_manager = container.settings_manager()
        self._course_path_services = container.course_path_services()
        self._evaluation_services = container.evaluation_services()
        self._grade_orchestrator = container.grade_orchestrator()

        self._event_bus = container.event_bus()

        self._init_controller()

        self._processing_grade_sub_section_update = False

    @override
    def _connect_upstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._event_bus.evaluation.dataChanged,
                                    slot=self._refresh_evaluation_id_combo_box)
        nuitka_helpers.safe_connect(signal=self._event_bus.course.geNoteImportCompleted,
                                    slot=self.schedule_grade_sub_section_update)
        nuitka_helpers.safe_connect(signal=self._event_bus.evaluation.templateConfigurationChanged,
                                    slot=self.schedule_grade_sub_section_update)
        nuitka_helpers.safe_connect(signal=self._event_bus.submission.correctionFileUpdated,
                                    slot=self.schedule_grade_sub_section_update)

    @override
    def _connect_downstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._section_view.evaluationIDChanged,
                                    slot=self._event_bus.selection_widget.evaluationIDChanged)

        nuitka_helpers.safe_connect(signal=self._section_view.moodleArchiveButtonClicked,
                                    slot=self._handle_moodle_button_clicked)
        nuitka_helpers.safe_connect(signal=self._section_view.genoteUpdateButtonClicked,
                                    slot=self._handle_genote_button_clicked)

    def update_selection_widgets(self) -> None:
        if self._workflow.course_id is not None:
            self._refresh_evaluation_id_combo_box()

    def synchronized_evaluation_id(self, evaluation_id: int | None) -> None:
        self._section_view.synchronized_evaluation_id(evaluation_id=evaluation_id)

    @Slot()
    def schedule_grade_sub_section_update(self):
        if not self._processing_grade_sub_section_update:
            self._processing_grade_sub_section_update = True

            QTimer.singleShot(0, self._perform_grade_sub_section_update)

    @Slot()
    def _handle_genote_button_clicked(self) -> None:
        if self._workflow.course_id is not None and self._workflow.evaluation_id is not None:
            with QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor):  # type: ignore
                message_dto = self._grade_orchestrator.update_genote_file(
                    course_id=self._workflow.course_id, evaluation_id=self._workflow.evaluation_id)
                self._event_bus.grade.geNoteUpdated.emit(message_dto)

    @Slot()
    def _handle_moodle_button_clicked(self) -> None:
        if self._workflow.course_id is not None and self._workflow.evaluation_id is not None:
            with QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor):  # type: ignore
                message_dto = self._grade_orchestrator.archive_moodle_correction(course_id=self._workflow.course_id,
                                                                   evaluation_id=self._workflow.evaluation_id)
                self._event_bus.grade.moodleFileArchived.emit(message_dto)

                self._update_moodle_subsection()

    @Slot()
    def _refresh_evaluation_id_combo_box(self) -> None:
        if self._workflow.course_id:
            evaluation_selection_dtos = self._evaluation_services.list_evaluation_selection_dtos(
                course_id=self._workflow.course_id)

            combo_box_payload = evaluation_payloads.get_evaluation_id_combo_box_payload(
                current_data_selection=self._settings_manager.restored_settings.evaluation_id_selected,
                evaluation_selection_dtos=evaluation_selection_dtos)
            self._section_view.populate_evaluation_id_combo_box(payload=combo_box_payload)

    def _perform_grade_sub_section_update(self):
        if not self._processing_grade_sub_section_update:
            return

        self._processing_grade_sub_section_update = False
        self._update_genote_subsection()
        self._update_moodle_subsection()

    def _update_genote_subsection(self) -> None:
        if self._workflow.course_id is not None and self._workflow.evaluation_id is not None:

            genote_directory = self._course_path_services.get_genote_directory(course_id=self._workflow.course_id)

            has_evaluation_correction_directory = self._grade_orchestrator.check_has_correction_evaluation_directory(
                course_id=self._workflow.course_id, evaluation_id=self._workflow.evaluation_id)
            template_is_configured = self._grade_orchestrator.get_template_configuration_state(
                evaluation_id=self._workflow.evaluation_id)
            genote_button_state = self._grade_orchestrator.get_genote_update_button_state(
                course_id=self._workflow.course_id, evaluation_id=self._workflow.evaluation_id)


            genote_label_text = GeNoteLabelText(directory=genote_directory,
                                                template_is_configured=template_is_configured,
                                                has_evaluation_correction_directory=has_evaluation_correction_directory)

            self._section_view.update_genote_label(label_text=genote_label_text)
            self._section_view.update_genote_update_button_state(is_enabled=genote_button_state)

        else:
            genote_label_text = GeNoteLabelText()
            self._section_view.update_genote_label(label_text=genote_label_text)
            self._section_view.update_genote_update_button_state(is_enabled=False)

    def _update_moodle_subsection(self) -> None:
        if self._workflow.course_id is not None and self._workflow.evaluation_id is not None:
            moodle_directory = self._grade_orchestrator.get_moodle_evaluation_correction_archive_directory(
                course_id=self._workflow.course_id, evaluation_id=self._workflow.evaluation_id)
            has_evaluation_correction_directory = self._grade_orchestrator.check_has_correction_evaluation_directory(
                course_id=self._workflow.course_id, evaluation_id=self._workflow.evaluation_id)

            moodle_label_text = MoodleCorrectionArchiveLabelText(
                archive_directory=moodle_directory,
                has_evaluation_correction_directory=has_evaluation_correction_directory)

            self._section_view.update_moodle_correction_path_label(label_text=moodle_label_text)
            self._section_view.update_moodle_archive_button_state(is_enabled=has_evaluation_correction_directory)

        else:
            moodle_label_text = MoodleCorrectionArchiveLabelText()
            self._section_view.update_moodle_correction_path_label(label_text=moodle_label_text)
            self._section_view.update_moodle_archive_button_state(is_enabled=False)


class GradeStatisticsController(BaseController):

    def __init__(self, section_view: "GradeStatisticsGroupBox", workflow: GradeTransactionWorkflow,
                 parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._section_view = section_view
        self._workflow = workflow

        self._settings_manager = container.settings_manager()
        self._course_path_services = container.course_path_services()
        self._evaluation_services = container.evaluation_services()
        self._grade_orchestrator = container.grade_orchestrator()

        self._event_bus = container.event_bus()

        self._init_controller()

        self._figure_dto_loaded = False

    @override
    def _connect_upstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._event_bus.settings.uiThemeChanged,
                                    slot=self._section_view.set_charts_theme)

    @override
    def _connect_downstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._section_view.launchStatsClicked, slot=self._launch_stats_generation)
        nuitka_helpers.safe_connect(signal=self._section_view.exportFiguresClicked, slot=self._save_figures)
        nuitka_helpers.safe_connect(signal=self._section_view.exportExcelClicked, slot=self._export_table_to_excel)

    @override
    def _refresh_view(self) -> None:
        self._refresh_chart_theme()
        self.refresh_save_path()

    def clear_figures(self) -> None:
        if self._figure_dto_loaded:
            self._section_view.clear_charts()
            self._figure_dto_loaded = False

    def refresh_save_path(self) -> None:
        if self._workflow.evaluation_id is not None and self._workflow.course_id is not None:
            save_path = self._grade_orchestrator.get_note_distribution_save_path(
                course_id=self._workflow.course_id, evaluation_id=self._workflow.evaluation_id)
            self._section_view.update_figures_save_path(save_path=f"{save_path}.png")

    @Slot()
    def _launch_stats_generation(self) -> None:
        if self._workflow.evaluation_id is not None and self._workflow.course_id is not None:

            with QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor):  # type: ignore
                grade_reference_plot_dto = self._grade_orchestrator.get_grade_reference_dto(
                    course_id=self._workflow.course_id, evaluation_id=self._workflow.evaluation_id)

                if grade_reference_plot_dto:
                    self._section_view.load_reference_grade_plot_data(grade_reference_plot_dto)

        self._figure_dto_loaded = True
        self._section_view.launch_stats_charts()

    @Slot()
    def _export_table_to_excel(self) -> None:
        if self._workflow.evaluation_id is not None and self._workflow.course_id is not None:
            with QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor):  # type: ignore
                grade_reference_plot_dto = self._grade_orchestrator.get_grade_reference_dto(
                    course_id=self._workflow.course_id, evaluation_id=self._workflow.evaluation_id)

                if grade_reference_plot_dto:
                    save_path = self._grade_orchestrator.get_note_distribution_save_path(
                        course_id=self._workflow.course_id, evaluation_id=self._workflow.evaluation_id)

                    export_path, _ = QFileDialog.getSaveFileName(self,
                                                                 "Sauvegarder la figure",
                                                                 f"{save_path}.xlsx",
                                                                 "Excel Files (*.xlsx)")
                    if export_path:
                        self._grade_orchestrator.export_table_to_excel(
                            grade_reference_plot_dto=grade_reference_plot_dto,
                            export_path=export_path)

    @Slot()
    def _save_figures(self) -> None:
        if self._workflow.course_id is not None and self._workflow.evaluation_id is not None:
            save_path = self._grade_orchestrator.get_note_distribution_save_path(
                course_id=self._workflow.course_id, evaluation_id=self._workflow.evaluation_id)

            self._section_view.save_figures(save_path=f"{save_path}.png")

    def _refresh_chart_theme(self) -> None:
        ui_theme = self._settings_manager.restored_settings.ui_theme
        self._section_view.set_charts_theme(theme_name=ui_theme)


class GradePageController(BaseController):

    def __init__(self, page_view: "GradePage", parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._page_view = page_view
        self._workflow = GradeTransactionWorkflow()

        self._course_selection_controller = CourseSelectionController(
            course_selection_group_box_view=self._page_view.course_selection_group_box)
        self._grade_management_controller = GradeManagementController(
            workflow=self._workflow, section_view=self._page_view.grade_management_group_box)
        self._grade_statistics_controller = GradeStatisticsController(
            workflow=self._workflow, section_view=self._page_view.grade_statistics_group_box)

        self._course_services = container.course_services()

        self._event_bus = container.event_bus()

        self._init_controller()

    @override
    def _connect_upstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._event_bus.selection_widget.courseIDChanged,
                                    slot= self._handle_course_id_changed)
        nuitka_helpers.safe_connect(signal=self._event_bus.selection_widget.evaluationIDChanged,
                                    slot=self._handle_evaluation_id_changed)

        nuitka_helpers.safe_connect(signal=self._event_bus.course.dataChanged,
                                    slot=self._refresh_view)
        nuitka_helpers.safe_connect(signal=self._event_bus.database.courseHasValidData,
                                    slot=self._toggle_ui_state)

    @Slot()
    @override
    def _refresh_view(self) -> None:
        self._course_selection_controller.refresh_combo_box_selection()
        self._course_services.check_valid_data()

    @Slot(object)
    def _handle_course_id_changed(self, course_id: int | None) -> None:
        if course_id != self._workflow.course_id:
            self._workflow.course_id = course_id

            self._grade_management_controller.update_selection_widgets()

            self._grade_management_controller.schedule_grade_sub_section_update()

            self._grade_statistics_controller.refresh_save_path()
            self._grade_statistics_controller.clear_figures()

    @Slot(object)
    def _handle_evaluation_id_changed(self, evaluation_id: int | None) -> None:
        if evaluation_id != self._workflow.evaluation_id:
            self._workflow.evaluation_id = evaluation_id

            self._grade_management_controller.synchronized_evaluation_id(evaluation_id=evaluation_id)

            self._grade_management_controller.schedule_grade_sub_section_update()

            self._grade_statistics_controller.refresh_save_path()
            self._grade_statistics_controller.clear_figures()

    @Slot(bool)
    def _toggle_ui_state(self, course_has_valid_data: bool) -> None:
        self._page_view.set_ui_state(enabled_page_widgets=course_has_valid_data)
