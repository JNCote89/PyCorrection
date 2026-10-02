import logging

from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QApplication

from src.py_correction.core import nuitka_helpers
from src.py_correction.core.dependency_injection import container
from src.py_correction.core.domains.archive.archive_dtos import ArchiveResponseDTO
from src.py_correction.core.domains.course.course_dtos import CourseCreateDTO, CourseResponseDTO
from src.py_correction.core.domains.course_path.course_path_dtos import GeNoteResponseDTO
from src.py_correction.core.domains.evaluation.evaluation_dtos import EvaluationTemplateCompletedResponseDTO
from src.py_correction.core.domains.grade.grade_dtos import (GeNoteUpdateFailedResponseDTO,
                                                             MoodleArchiveCompletedResponseDTO)
from src.py_correction.core.domains.reference.reference_dtos import DryRunWarningResponseDTO
from src.py_correction.core.domains.student.student_dtos import StudentCreateDTO
from src.py_correction.core.domains.submission.submission_dtos import (MoodleImportCompletedResponseDTO,
                                                                       MoodleMakeCorrectionFileResponseDTO)
from src.py_correction.ui.components.default_widgets.message_boxes import DefaultInfoMessageBox
from src.py_correction.ui.feedbacks.messages.base_message import BaseMessageText
from src.py_correction.ui.feedbacks.messages.database_messages import CourseIntegrityFailedMessage
from src.py_correction.ui.feedbacks.messages.import_messages import (CourseArchiveCompletedMessage,
                                                                     CourseFormCompletedMessage,
                                                                     CourseRestoreCompletedMessage,
                                                                     EvaluationFormCompletedMessage,
                                                                     EvaluationTemplateCompletedMessage,
                                                                     GeNoteCompletedMessage, GeNoteFailedMessage,
                                                                     GeNoteUpdateMessage,
                                                                     MakeCorrectionFileCompletedMessage,
                                                                     MakeCorrectionFileFailedMessage,
                                                                     MoodleArchiveCompletedMessage,
                                                                     MoodleImportCompletedMessage,
                                                                     StudentFormCompletedMessage)
from src.py_correction.ui.feedbacks.messages.warning_messages import ReferenceVerificationDryRunMessage

logger = logging.getLogger(__name__)


class UINotificationManager(QObject):

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent=parent)
        self.settings_manager = container.settings_manager()

        self._event_bus = container.event_bus()

        self._connect_signals()

    def _connect_signals(self) -> None:

        # --- Course ---
        nuitka_helpers.safe_connect(signal=self._event_bus.course.geNoteImportFailed,
                                    slot=self._on_genote_import_failed)
        nuitka_helpers.safe_connect(signal=self._event_bus.course.geNoteImportCompleted,
                                    slot=self._on_genote_import_completed)
        nuitka_helpers.safe_connect(signal=self._event_bus.course.formImportCompleted,
                                    slot=self._on_course_form_import_completed)

        # --- Database ---
        nuitka_helpers.safe_connect(signal=self._event_bus.database.courseIntegrityFailed,
                                    slot=self._on_course_integrity_failed)

        # --- Evaluation ---
        nuitka_helpers.safe_connect(signal=self._event_bus.evaluation.formImportCompleted,
                                    slot=self._on_evaluation_form_import_completed)
        nuitka_helpers.safe_connect(signal=self._event_bus.evaluation.templateFileImportCompleted,
                                    slot=self._on_template_import_completed)

        # --- Student ---
        nuitka_helpers.safe_connect(signal=self._event_bus.student.formImportCompleted,
                                    slot=self._on_student_form_import_completed)

        # --- Submission ---
        nuitka_helpers.safe_connect(signal=self._event_bus.submission.moodleImportCompleted,
                                    slot=self._on_moodle_import_completed)
        nuitka_helpers.safe_connect(signal=self._event_bus.submission.makeCorrectionFileCompleted,
                                    slot=self._on_correction_file_completed)
        nuitka_helpers.safe_connect(signal=self._event_bus.submission.makeCorrectionFileFailed,
                                    slot=self._on_correction_file_failed)

        # --- Reference ---
        nuitka_helpers.safe_connect(signal=self._event_bus.reference.dryRunWarningEmitted,
                                    slot=self._on_dry_run_warning)

        # --- Grade ---
        nuitka_helpers.safe_connect(signal=self._event_bus.grade.geNoteUpdated,
                                    slot=self._on_genote_updated)
        nuitka_helpers.safe_connect(signal=self._event_bus.grade.moodleFileArchived,
                                    slot=self._on_moodle_archive_completed)

        # --- Archive ---
        nuitka_helpers.safe_connect(signal=self._event_bus.archive.courseArchiveCompleted,
                                    slot=self._on_course_archive_completed)
        nuitka_helpers.safe_connect(signal=self._event_bus.archive.courseRestoreCompleted,
                                    slot=self._on_course_restore_completed)

    @Slot(str)
    def _on_genote_import_failed(self, wrong_filename: str) -> None:
        message = GeNoteFailedMessage(wrong_filename=wrong_filename)
        self._handle_user_notification(message)

    @Slot(GeNoteResponseDTO)
    def _on_genote_import_completed(self, genote_response_dto: GeNoteResponseDTO) -> None:
        message = GeNoteCompletedMessage(new_source_path=genote_response_dto.new_source_path,
                                         grade_directory_path=genote_response_dto.grade_directory_path)
        self._handle_user_notification(message=message)

    @Slot(CourseResponseDTO)
    def _on_course_form_import_completed(self, course_response_dto: CourseResponseDTO) -> None:
        message = CourseFormCompletedMessage(course_code=course_response_dto.code,
                                             course_name=course_response_dto.name,
                                             course_group=course_response_dto.group,
                                             course_semester=course_response_dto.semester)
        self._handle_user_notification(message=message)

    @Slot(CourseCreateDTO)
    def _on_course_integrity_failed(self, course_input_dto: CourseCreateDTO) -> None:
        message = CourseIntegrityFailedMessage(course_code=course_input_dto.code,
                                               course_name=course_input_dto.name,
                                               course_semester=course_input_dto.semester,
                                               course_group=course_input_dto.group)
        self._handle_user_notification(message=message)

    @Slot(str)
    def _on_evaluation_form_import_completed(self, evaluation_title: str) -> None:
        message = EvaluationFormCompletedMessage(evaluation_title=evaluation_title)
        self._handle_user_notification(message=message)

    @Slot(EvaluationTemplateCompletedResponseDTO)
    def _on_template_import_completed(self, import_response_dto: EvaluationTemplateCompletedResponseDTO
                                      ) -> None:
        message = EvaluationTemplateCompletedMessage(original_path=import_response_dto.original_path,
                                                     template_directory=import_response_dto.template_directory)
        self._handle_user_notification(message=message)

    @Slot(StudentCreateDTO)
    def _on_student_form_import_completed(self, student_dto: StudentCreateDTO) -> None:
        message = StudentFormCompletedMessage(cip=student_dto.cip, first_name=student_dto.first_name,
                                              last_name=student_dto.last_name)
        self._handle_user_notification(message=message)

    @Slot(MoodleImportCompletedResponseDTO)
    def _on_moodle_import_completed(self, import_response_dto: MoodleImportCompletedResponseDTO) -> None:
        message = MoodleImportCompletedMessage(
            source_zip_file=import_response_dto.source_zip_file,
            target_extraction_directory=import_response_dto.target_extraction_directory,
            submission_archive_directory=import_response_dto.submission_archive_directory,
            new_archive_name=import_response_dto.new_archive_name)
        self._handle_user_notification(message=message)

    @Slot(MoodleMakeCorrectionFileResponseDTO)
    def _on_correction_file_completed(self, response_dto: MoodleMakeCorrectionFileResponseDTO) -> None:
        message = MakeCorrectionFileCompletedMessage(
            student_names=response_dto.student_names,
            evaluation_correction_directory=response_dto.evaluation_correction_directory)
        self._handle_user_notification(message=message)

    @Slot(MoodleMakeCorrectionFileResponseDTO)
    def _on_correction_file_failed(self, response_dto: MoodleMakeCorrectionFileResponseDTO) -> None:
        message = MakeCorrectionFileFailedMessage(
            student_names=response_dto.student_names,
            evaluation_correction_directory=response_dto.evaluation_correction_directory)
        self._handle_user_notification(message=message)

    @Slot(DryRunWarningResponseDTO)
    def _on_dry_run_warning(self, warning_dto: DryRunWarningResponseDTO) -> None:
        message = ReferenceVerificationDryRunMessage(course_id=warning_dto.course_id,
                                                     evaluation_id=warning_dto.evaluation_id,
                                                     student_id=warning_dto.student_id)
        self._handle_user_notification(message=message)

    @Slot(GeNoteUpdateFailedResponseDTO)
    def _on_genote_updated(self, failed_dto: GeNoteUpdateFailedResponseDTO) -> None:
        message = GeNoteUpdateMessage(failed_operations=failed_dto.failed_operations,
                                      evaluation_title=failed_dto.evaluation_title)
        self._handle_user_notification(message=message)

    @Slot(MoodleArchiveCompletedResponseDTO)
    def _on_moodle_archive_completed(self, message_dto: MoodleArchiveCompletedResponseDTO) -> None:
        message = MoodleArchiveCompletedMessage(source_file=message_dto.source_file,
                                                destination_directory=message_dto.destination_directory)
        self._handle_user_notification(message=message)

    @Slot(ArchiveResponseDTO)
    def _on_course_archive_completed(self, response_dto: ArchiveResponseDTO) -> None:
        message = CourseArchiveCompletedMessage(course_name=response_dto.course_name,
                                                new_directory=response_dto.new_directory)
        self._handle_user_notification(message=message)

    @Slot(ArchiveResponseDTO)
    def _on_course_restore_completed(self, response_dto: ArchiveResponseDTO) -> None:
        message = CourseRestoreCompletedMessage(course_name=response_dto.course_name,
                                                new_directory=response_dto.new_directory)
        self._handle_user_notification(message=message)

    def _handle_user_notification(self, message: BaseMessageText) -> None:
        QApplication.restoreOverrideCursor()

        message_box_widget = DefaultInfoMessageBox(window_title=message.title)
        logger.info(message.log_text)

        if self.settings_manager.restored_settings.pop_up_notifications_state:
            message_box_widget.setText(message.popup_text)
            message_box_widget.exec()
