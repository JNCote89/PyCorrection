from pathlib import Path

from PySide6.QtCore import QCoreApplication, QObject, Signal

from src.py_correction.core.domains.archive.archive_dtos import ArchiveResponseDTO
from src.py_correction.core.domains.course.course_dtos import CourseCreateDTO, CourseResponseDTO
from src.py_correction.core.domains.course_path.course_path_dtos import GeNoteResponseDTO
from src.py_correction.core.domains.evaluation.evaluation_dtos import EvaluationTemplateCompletedResponseDTO
from src.py_correction.core.domains.grade.grade_dtos import (GeNoteUpdateFailedResponseDTO,
                                                             MoodleArchiveCompletedResponseDTO)
from src.py_correction.core.domains.reference.reference_dtos import DryRunWarningResponseDTO
from src.py_correction.core.domains.shared.shared_enums import AutofillOptions
from src.py_correction.core.domains.student.student_dtos import StudentCreateDTO
from src.py_correction.core.domains.submission.submission_dtos import (MoodleImportCompletedResponseDTO,
                                                                       MoodleMakeCorrectionFileResponseDTO)
from src.py_correction.core.theme_manager import ThemeOptions
from src.py_correction.engine.reference.csl.csl_enum import CitationStyle


class CourseBus(QObject):
    dataChanged = Signal()
    newCourseIDImported = Signal(int)
    geNoteImportFailed = Signal(str)
    geNoteImportCompleted = Signal(GeNoteResponseDTO)
    formImportCompleted = Signal(CourseResponseDTO)


class StudentBus(QObject):
    dataChanged = Signal()
    formImportCompleted = Signal(StudentCreateDTO)


class EvaluationBus(QObject):
    dataChanged = Signal()
    formImportCompleted = Signal(str)
    templateFileImportCompleted = Signal(EvaluationTemplateCompletedResponseDTO)
    templateConfigurationChanged = Signal()


class DatabaseBus(QObject):
    courseIntegrityFailed = Signal(CourseCreateDTO)
    courseHasValidData = Signal(bool)
    courseArchived = Signal(int)
    courseRestored = Signal()


class SubmissionBus(QObject):
    moodleImportCompleted = Signal(MoodleImportCompletedResponseDTO)
    makeCorrectionFileCompleted = Signal(MoodleMakeCorrectionFileResponseDTO)
    makeCorrectionFileFailed = Signal(MoodleMakeCorrectionFileResponseDTO)
    correctionFileUpdated = Signal()
    submissionFileUpdated = Signal()


class SettingsManagerBus(QObject):
    userRootDirectoryChanged = Signal(Path)
    uiThemeChanged = Signal(ThemeOptions)
    evaluationAutofillChanged = Signal(AutofillOptions)
    citationStyleChanged = Signal(CitationStyle)
    popupNotificationChanged = Signal(bool)
    manualSectionExpansionChanged = Signal(bool)


class SelectionWidgetBus(QObject):
    courseIDChanged = Signal(object)
    semesterLabelChanged = Signal(object)
    evaluationIDChanged = Signal(object)
    studentIDChanged = Signal(object)


class ReferenceBus(QObject):
    dryRunWarningEmitted = Signal(DryRunWarningResponseDTO)

class GradeBus(QObject):
    geNoteUpdated = Signal(GeNoteUpdateFailedResponseDTO)
    moodleFileArchived = Signal(MoodleArchiveCompletedResponseDTO)

class ArchiveBus(QObject):
    courseArchiveCompleted = Signal(ArchiveResponseDTO)
    courseRestoreCompleted = Signal(ArchiveResponseDTO)


class EventBus(QObject):

    def __init__(self) -> None:
        app = QCoreApplication.instance()
        super().__init__(parent=app)

        self.course = CourseBus(parent=self)
        self.selection_widget = SelectionWidgetBus(parent=self)
        self.student = StudentBus(parent=self)
        self.evaluation = EvaluationBus(parent=self)
        self.reference = ReferenceBus(parent=self)
        self.submission = SubmissionBus(parent=self)
        self.database = DatabaseBus(parent=self)
        self.settings = SettingsManagerBus(parent=self)
        self.grade = GradeBus(parent=self)
        self.archive = ArchiveBus(parent=self)
