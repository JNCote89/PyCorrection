from dataclasses import dataclass, field
import logging
from pathlib import Path
import shutil
from typing import TYPE_CHECKING

from src.py_correction.engine.moodle.moodle_helpers import (get_student_name_from_moodle_directory,
                                                            get_unique_student_directory_count)
from src.py_correction.io_operations.archives import (extract_archives, get_overwrite_directory_name_conflicts,
                                                      move_to_archives_with_timestamp)

if TYPE_CHECKING:
    from src.py_correction.core.event_bus import EventBus
    from src.py_correction.services.domains.course.course_services import CourseServices
    from src.py_correction.services.domains.evaluation.evaluation_services import EvaluationServices
    from src.py_correction.services.domains.course_path.course_path_services import CoursePathServices
    from src.py_correction.services.path_resolver.path_resolver import PathResolver

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MoodleSubmissionZipImportPreparation:
    zip_file_path: Path
    evaluation_submission_directory: Path
    submissions_archives_directory: Path | None
    directory_name_conflicts: list[str] | None = field(default_factory=list)


@dataclass(frozen=True)
class DirectoryCountLabel:
    evaluation_submission_directory: Path | None
    submission_count: int


@dataclass
class CorrectionFileOperationResults:
    students_completed: list[str]
    students_failed: list[str]
    evaluation_correction_directory: Path


class SubmissionOrchestrator:

    def __init__(self, course_services: "CourseServices",
                 evaluation_services: "EvaluationServices", course_path_services: "CoursePathServices",
                 path_resolver: "PathResolver",
                 event_bus: "EventBus"):
        self._course_services = course_services
        self._evaluation_services = evaluation_services
        self._course_path_services = course_path_services
        self._path_resolver = path_resolver

        self._event_bus = event_bus

    def prepare_moodle_submission_zip_import(self, zip_file_path: Path, evaluation_id: int,
                                             course_id: int) -> MoodleSubmissionZipImportPreparation | None:
        evaluation_submission_directory = self._path_resolver.get_evaluation_submission_directory(
            evaluation_id=evaluation_id, course_id=course_id)

        submissions_archive_directory = self._course_path_services.get_submission_archives_directory(
            course_id=course_id)

        if evaluation_submission_directory:
            overwrite_directory_name_conflicts = get_overwrite_directory_name_conflicts(
                archives_path=zip_file_path, target_path=evaluation_submission_directory)
        else:
            overwrite_directory_name_conflicts = None

        if evaluation_submission_directory is not None and submissions_archive_directory is not None:
            return MoodleSubmissionZipImportPreparation(zip_file_path=zip_file_path,
                                                        evaluation_submission_directory=evaluation_submission_directory,
                                                        submissions_archives_directory=submissions_archive_directory,
                                                        directory_name_conflicts=overwrite_directory_name_conflicts)
        return None

    @staticmethod
    def extract_submission_archive(moodle_submission_zip_import_preparation: MoodleSubmissionZipImportPreparation,
                                   overwrite_permission: bool) -> None:
        if overwrite_permission:
            extract_archives(archive_path=moodle_submission_zip_import_preparation.zip_file_path,
                             target_directory=moodle_submission_zip_import_preparation.evaluation_submission_directory)
        else:
            extract_archives(archive_path=moodle_submission_zip_import_preparation.zip_file_path,
                             target_directory=moodle_submission_zip_import_preparation.evaluation_submission_directory,
                             skip_directory_names=moodle_submission_zip_import_preparation.directory_name_conflicts)

    @staticmethod
    def store_submission_archive(moodle_submission_zip_import_preparation: MoodleSubmissionZipImportPreparation
                                 ) -> Path | None:
        if moodle_submission_zip_import_preparation.submissions_archives_directory is None:
            return None

        new_archive_path_name = move_to_archives_with_timestamp(
            source_file=moodle_submission_zip_import_preparation.zip_file_path,
            archive_directory=moodle_submission_zip_import_preparation.submissions_archives_directory)

        return new_archive_path_name

    def get_directory_count_label(self, course_id: int, evaluation_id: int) -> DirectoryCountLabel:
        evaluation_submission_directory = self._path_resolver.get_evaluation_submission_directory(
            course_id=course_id, evaluation_id=evaluation_id)

        if evaluation_submission_directory is not None:
            submission_count = get_unique_student_directory_count(evaluation_submission_directory)
            return DirectoryCountLabel(evaluation_submission_directory=evaluation_submission_directory,
                                       submission_count=submission_count)
        else:
            return DirectoryCountLabel(evaluation_submission_directory=None,
                                       submission_count=0)

    def get_submission_state(self, course_id: int, evaluation_id: int) -> bool:
        template_name = self._evaluation_services.get_evaluation_template_filename(evaluation_id=evaluation_id)

        submission_count_label = self.get_directory_count_label(course_id=course_id, evaluation_id=evaluation_id)

        if (template_name and submission_count_label.evaluation_submission_directory and
                submission_count_label.submission_count > 0):
            return True

        return False

    def make_student_correction_file(self, course_id: int,
                                     evaluation_id: int) -> CorrectionFileOperationResults | None:
        evaluation_submission_directory = self._path_resolver.get_evaluation_submission_directory(
            course_id=course_id, evaluation_id=evaluation_id)

        evaluation_correction_directory = self._path_resolver.get_evaluation_correction_directory(
            course_id=course_id, evaluation_id=evaluation_id)

        if evaluation_submission_directory is None or evaluation_correction_directory is None:
            return None

        evaluation_submission_directory.mkdir(exist_ok=True, parents=True)
        evaluation_submission_directory.mkdir(exist_ok=True, parents=True)

        # If the student submit two different kind of submission (e.g., text and files), Moodle split them in two
        # separate folders. Yet, we don't want two different correction directories, so we keep only one directory to
        # copy.
        student_names = set()

        results = CorrectionFileOperationResults(students_completed=[], students_failed=[],
                                                 evaluation_correction_directory=evaluation_correction_directory)

        for student_evaluation_directory in evaluation_submission_directory.iterdir():
            student_name = get_student_name_from_moodle_directory(moodle_directory=student_evaluation_directory)

            if student_name in student_names:
                continue

            student_names.add(student_name)

            if self._setup_student_correction_file(student_evaluation_directory=student_evaluation_directory,
                                                   student_name=student_name,
                                                   evaluation_id=evaluation_id,
                                                   evaluation_correction_directory=evaluation_correction_directory):
                results.students_completed.append(student_name)
            else:
                results.students_failed.append(student_name)

        return results

    def _setup_student_correction_file(self, student_evaluation_directory: Path, student_name: str,
                                       evaluation_id: int,
                                       evaluation_correction_directory: Path) -> bool:
        evaluation_template_file_path = self._evaluation_services.get_evaluation_template_file_path(
            evaluation_id=evaluation_id)
        if evaluation_template_file_path is None:
            return False

        student_evaluation_directory_name = student_evaluation_directory.name

        template_student_name = f"{student_name}_{evaluation_template_file_path.name}"
        target_directory = evaluation_correction_directory / student_evaluation_directory_name
        target_file = target_directory / template_student_name

        try:
            target_directory.mkdir(parents=True, exist_ok=False)
            shutil.copy(evaluation_template_file_path, target_file)
            return True
        except FileExistsError:
            return False