from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, override

from PySide6.QtCore import QTimer, Qt, Slot
from PySide6.QtWidgets import QApplication, QWidget

from src.py_correction.core import nuitka_helpers
from src.py_correction.core.dependency_injection import container
from src.py_correction.core.domains.submission.submission_dtos import (MoodleImportCompletedResponseDTO,
                                                                       MoodleMakeCorrectionFileResponseDTO)
from src.py_correction.ui.components.base_components.base_controller import BaseController
from src.py_correction.ui.components.default_widgets.message_boxes import DefaultQuestionMessageBox
from src.py_correction.ui.components.payload_builders import evaluation_payloads
from src.py_correction.ui.components.shared_components.course_selection.course_selection_controller import (
    CourseSelectionController)
from src.py_correction.ui.components.shared_components.workflow.workflow_mixin import ResetWorkflowMixin
from src.py_correction.ui.feedbacks.labels.directory_labels import (SubmissionCountLabelText, TemplateFilenameLabelText)
from src.py_correction.ui.feedbacks.messages.confirmation_messages import DirectoryOverwriteWarningMessage

if TYPE_CHECKING:
    from src.py_correction.ui.pages.submission.submission_page import SubmissionPage
    from src.py_correction.ui.pages.submission.submission_sections import SubmissionsManagementGroupBox


@dataclass
class SubmissionTransactionWorkflow(ResetWorkflowMixin):
    course_id: int | None = field(default=None)
    evaluation_id: int | None = field(default=None)

    evaluation_submission_directory: Path | None = field(default=None)


class SubmissionManagementController(BaseController):

    def __init__(self, section_view: "SubmissionsManagementGroupBox", workflow: SubmissionTransactionWorkflow,
                 parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._section_view = section_view
        self._workflow = workflow

        self._settings_manager = container.settings_manager()
        self._student_services = container.student_services()
        self._course_services = container.course_services()
        self._evaluation_services = container.evaluation_services()
        self._course_path_services = container.course_path_services()
        self._submission_orchestrator = container.submission_orchestrator()

        self._event_bus = container.event_bus()

        self._init_controller()

        self._processing_submission_sub_section_update = False

    @override
    def _connect_upstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._event_bus.evaluation.dataChanged,
                                    slot=self._refresh_evaluation_id_combo_box)
        nuitka_helpers.safe_connect(signal=self._event_bus.evaluation.templateConfigurationChanged,
                                    slot=self._update_correction_template_name_label)

    @override
    def _connect_downstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._section_view.evaluationIDChanged,
                                    slot=self._event_bus.selection_widget.evaluationIDChanged)

        nuitka_helpers.safe_connect(signal=self._section_view.moodleZipFileSubmitted,
                                    slot=self._handle_moodle_submission_zip_import)
        nuitka_helpers.safe_connect(signal=self._section_view.makeStudentCorrectionButtonClicked,
                                    slot=self._make_student_correction_file)

    @override
    def _refresh_view(self) -> None:
        self._update_make_student_correction_file_button_state()

    def update_selection_widgets(self) -> None:
        if self._workflow.course_id is not None:
            self._refresh_evaluation_id_combo_box()

    def synchronized_evaluation_id(self, evaluation_id: int | None) -> None:
        self._section_view.synchronized_evaluation_id(evaluation_id=evaluation_id)

    def schedule_submission_sub_section_update(self):
        if not self._processing_submission_sub_section_update:
            self._processing_submission_sub_section_update = True

            QTimer.singleShot(0, self._perform_submission_sub_section_update)

    @Slot(Path)
    def _handle_moodle_submission_zip_import(self, zip_file_path: Path) -> None:
        if self._workflow.course_id is not None and self._workflow.evaluation_id is not None:
            with QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor):  # type: ignore
                prepare_import = self._submission_orchestrator.prepare_moodle_submission_zip_import(
                    zip_file_path=zip_file_path,
                    evaluation_id=self._workflow.evaluation_id,
                    course_id=self._workflow.course_id)

                if prepare_import and prepare_import.directory_name_conflicts is not None:
                    overwrite_message = DirectoryOverwriteWarningMessage(
                        overwritten_directories=prepare_import.directory_name_conflicts)

                    message_box = DefaultQuestionMessageBox(window_title=overwrite_message.title,
                                                            html_message=overwrite_message.html_text)

                    overwrite_permission = message_box.get_reply_bool()
                else:
                    overwrite_permission = True

                if prepare_import:
                    self._submission_orchestrator.extract_submission_archive(
                        moodle_submission_zip_import_preparation=prepare_import,
                        overwrite_permission=overwrite_permission)

                    new_archive_path = self._submission_orchestrator.store_submission_archive(
                        moodle_submission_zip_import_preparation=prepare_import)

                    if new_archive_path:
                        import_response_dto = MoodleImportCompletedResponseDTO(
                            source_zip_file=prepare_import.zip_file_path,
                            target_extraction_directory=prepare_import.evaluation_submission_directory,
                            submission_archive_directory=prepare_import.submissions_archives_directory,
                            new_archive_name=new_archive_path.name)

                        self._event_bus.submission.moodleImportCompleted.emit(import_response_dto)
                        self._event_bus.submission.submissionFileUpdated.emit()

                        self._update_directory_count_label()

    @Slot()
    def _make_student_correction_file(self) -> None:
        if self._workflow.course_id is not None and self._workflow.evaluation_id is not None:
            with QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor):  # type: ignore
                results = self._submission_orchestrator.make_student_correction_file(
                    course_id=self._workflow.course_id,
                    evaluation_id=self._workflow.evaluation_id)

                if results and results.students_completed:
                    completed_response_dto = MoodleMakeCorrectionFileResponseDTO(
                        student_names=results.students_completed,
                        evaluation_correction_directory=results.evaluation_correction_directory)
                    self._event_bus.submission.makeCorrectionFileCompleted.emit(completed_response_dto)
                    self._event_bus.submission.correctionFileUpdated.emit()

                if results and results.students_failed:
                    failed_response_dto = MoodleMakeCorrectionFileResponseDTO(
                        student_names=results.students_failed,
                        evaluation_correction_directory=results.evaluation_correction_directory)
                    self._event_bus.submission.makeCorrectionFileFailed.emit(failed_response_dto)

    def _refresh_evaluation_id_combo_box(self) -> None:
        course_id = self._workflow.course_id
        if course_id is not None:
            evaluation_selection_dtos = self._evaluation_services.list_evaluation_selection_dtos(course_id=course_id)

            combo_box_payload = evaluation_payloads.get_evaluation_id_combo_box_payload(
                current_data_selection=self._settings_manager.restored_settings.evaluation_id_selected,
                evaluation_selection_dtos=evaluation_selection_dtos)

            self._section_view.populate_evaluation_id_combo_box(payload=combo_box_payload)

    def _perform_submission_sub_section_update(self):
        if not self._processing_submission_sub_section_update:
            return

        self._processing_submission_sub_section_update = False

        self._update_correction_template_name_label()
        self._update_directory_count_label()
        self._update_make_student_correction_file_button_state()

    def _update_correction_template_name_label(self) -> None:
        if self._workflow.evaluation_id is not None:
            template_filename = self._evaluation_services.get_evaluation_template_filename(
                evaluation_id=self._workflow.evaluation_id)

            filename_label_message = TemplateFilenameLabelText(template_filename=template_filename)
            self._section_view.update_template_filename_label(label_text=filename_label_message)

            self._update_make_student_correction_file_button_state()

    def _update_directory_count_label(self) -> None:
        if self._workflow.course_id is not None and self._workflow.evaluation_id is not None:
            directory_count_label = self._submission_orchestrator.get_directory_count_label(
                course_id=self._workflow.course_id,
                evaluation_id=self._workflow.evaluation_id)
            if directory_count_label:
                self._workflow.evaluation_submission_directory = directory_count_label.evaluation_submission_directory

                submission_count_label_message = SubmissionCountLabelText(
                    directory=directory_count_label.evaluation_submission_directory,
                    submission_count=directory_count_label.submission_count)

                self._section_view.update_submission_count_label(label_text=submission_count_label_message)
                self._update_make_student_correction_file_button_state()

    def _update_make_student_correction_file_button_state(self) -> None:
        if self._workflow.course_id is not None and self._workflow.evaluation_id is not None:
            submission_enabled_state = self._submission_orchestrator.get_submission_state(
                course_id=self._workflow.course_id,
                evaluation_id=self._workflow.evaluation_id)
            self._section_view.update_make_student_correction_file_button(state=submission_enabled_state)

        else:
            self._section_view.update_make_student_correction_file_button(state=False)


class SubmissionPageController(BaseController):

    def __init__(self, page_view: "SubmissionPage", parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._page_view = page_view
        self._workflow = SubmissionTransactionWorkflow()

        self._course_selection_controller = CourseSelectionController(
            course_selection_group_box_view=self._page_view.course_selection_group_box)
        self._submission_management_controller = SubmissionManagementController(
            workflow=self._workflow, section_view=self._page_view.submission_management_group_box)

        self._course_services = container.course_services()
        self._event_bus = container.event_bus()

        self._init_controller()

    @override
    def _connect_upstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._event_bus.selection_widget.courseIDChanged,
                                    slot=self._handle_course_id_changed)
        nuitka_helpers.safe_connect(signal=self._event_bus.selection_widget.evaluationIDChanged,
                                    slot=self._handle_evaluation_id_changed)

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

            self._submission_management_controller.update_selection_widgets()

            self._submission_management_controller.schedule_submission_sub_section_update()

    @Slot(object)
    def _handle_evaluation_id_changed(self, evaluation_id: int | None) -> None:
        if evaluation_id != self._workflow.evaluation_id:
            self._workflow.evaluation_id = evaluation_id

            self._submission_management_controller.synchronized_evaluation_id(evaluation_id=evaluation_id)

            self._submission_management_controller.schedule_submission_sub_section_update()

    @Slot(bool)
    def _toggle_ui_state(self, course_has_valid_data: bool) -> None:
        self._page_view.set_ui_state(enabled_page_widgets=course_has_valid_data)
