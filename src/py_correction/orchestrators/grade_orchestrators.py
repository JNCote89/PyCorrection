from dataclasses import asdict
import logging
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

from src.py_correction.core.domains.grade.grade_dtos import (GeNoteTransactionDTO, GeNoteUpdateFailedResponseDTO,
                                                             MoodleArchiveCompletedResponseDTO, UpdateGradeDTO)
from src.py_correction.core.domains.reference.reference_figures_dtos import GradeReferencePlotDTO
from src.py_correction.engine.genote.genote_operations import GeNoteGradeFileOperations
from src.py_correction.engine.moodle import moodle_helpers
from src.py_correction.engine.template import template_operations
from src.py_correction.io_operations import archives

if TYPE_CHECKING:
    from src.py_correction.core.event_bus import EventBus
    from src.py_correction.services.domains.course.course_services import CourseServices
    from src.py_correction.services.domains.evaluation.evaluation_services import EvaluationServices
    from src.py_correction.services.domains.course_path.course_path_services import CoursePathServices
    from src.py_correction.services.domains.student.student_evaluation_services import StudentEvaluationServices
    from src.py_correction.services.domains.course.course_student_services import CourseStudentServices
    from src.py_correction.services.path_resolver.path_resolver import PathResolver

logger = logging.getLogger(__name__)


class GradeOrchestrator:

    def __init__(self, course_services: "CourseServices",
                 evaluation_services: "EvaluationServices", course_path_services: "CoursePathServices",
                 student_evaluation_services: "StudentEvaluationServices",
                 course_student_services: "CourseStudentServices",
                 path_resolver: "PathResolver",
                 event_bus: "EventBus"):
        self._course_services = course_services
        self._evaluation_services = evaluation_services
        self._course_path_services = course_path_services
        self._student_evaluation_services = student_evaluation_services
        self._path_resolver = path_resolver
        self._course_student_services = course_student_services

        self._event_bus = event_bus

    def get_moodle_evaluation_correction_archive_directory(self, course_id: int, evaluation_id: int) -> Path | None:
        correction_archive_directory = self._course_path_services.get_correction_archives_directory(course_id=course_id)
        if correction_archive_directory is None:
            return None

        evaluation_title = self._evaluation_services.get_evaluation_title(evaluation_id=evaluation_id)

        if evaluation_title is None:
            return None

        archive_directory = correction_archive_directory / evaluation_title
        archive_directory.mkdir(parents=True, exist_ok=True)

        if archive_directory.exists():
            return archive_directory

        return None

    def get_template_configuration_state(self, evaluation_id: int) -> bool:
        evaluation_template_dto = self._evaluation_services.get_evaluation_template_dto(evaluation_id=evaluation_id)
        if evaluation_template_dto:
            return (bool(evaluation_template_dto.filename) and bool (evaluation_template_dto.row_keyword)
                    and bool(evaluation_template_dto.column_keyword))
        return False

    def get_genote_update_button_state(self, course_id: int, evaluation_id: int) -> bool:
        correction_path = self._path_resolver.get_evaluation_correction_directory(course_id=course_id,
                                                                                  evaluation_id=evaluation_id)
        genote_directory = self._course_path_services.get_genote_directory(course_id=course_id)

        template_is_configured = self.get_template_configuration_state(evaluation_id=evaluation_id)

        if correction_path is not None and genote_directory is not None:
            return correction_path.exists() and genote_directory.exists() and template_is_configured

        return False

    def update_genote_file(self, course_id: int, evaluation_id: int) -> GeNoteUpdateFailedResponseDTO | None:
        correction_path = self._path_resolver.get_evaluation_correction_directory(course_id=course_id,
                                                                                  evaluation_id=evaluation_id)

        evaluation_template_dto = self._evaluation_services.get_evaluation_template_dto(evaluation_id=evaluation_id)

        genote_file = self._load_genote_file_operations(course_id=course_id)

        student_genote_grades = []
        student_database_grades = []

        if (correction_path and evaluation_template_dto and evaluation_template_dto.filename
                and evaluation_template_dto.evaluation_title):

            for student_evaluation_directory in correction_path.iterdir():
                student_name = moodle_helpers.get_student_name_from_moodle_directory(
                    moodle_directory=student_evaluation_directory)

                excel_template_path = student_evaluation_directory / f"{student_name}_{evaluation_template_dto.filename}"

                student_grade = template_operations.return_student_grade_from_correction_file(
                    template_path=excel_template_path, template_sheet=evaluation_template_dto.template_sheet,
                    row_keyword=evaluation_template_dto.row_keyword,
                    column_keyword=evaluation_template_dto.column_keyword)

                student_genote_grades.append(GeNoteTransactionDTO(
                    student_name=student_name, student_grade=student_grade,
                    evaluation_title=evaluation_template_dto.evaluation_title))

                student_database_grades.append(UpdateGradeDTO(evaluation_id=evaluation_id,
                                                              first_name=student_name.split(',')[
                                                                  1].strip(),
                                                              last_name=student_name.split(',')[
                                                                  0].strip(),
                                                              grade=student_grade))

            if student_genote_grades:
                self._student_evaluation_services.add_grade_from_name(update_grade_dtos=student_database_grades)
                failed_operations = genote_file.add_grades(genote_transaction_dtos=student_genote_grades)

                return GeNoteUpdateFailedResponseDTO(failed_operations=failed_operations,
                                                     evaluation_title=evaluation_template_dto.evaluation_title)

        return None

    def check_has_correction_evaluation_directory(self, course_id: int, evaluation_id: int) -> bool:
        evaluation_correction_directory = self._path_resolver.get_evaluation_correction_directory(
            course_id=course_id, evaluation_id=evaluation_id)

        if evaluation_correction_directory is not None:
            return evaluation_correction_directory.exists()

        return False

    def archive_moodle_correction(self, course_id: int, evaluation_id: int) -> MoodleArchiveCompletedResponseDTO | None:
        evaluation_correction_directory = self._path_resolver.get_evaluation_correction_directory(
            course_id=course_id, evaluation_id=evaluation_id)

        moodle_evaluation_correction_archive = self.get_moodle_evaluation_correction_archive_directory(
            course_id=course_id, evaluation_id=evaluation_id)

        if moodle_evaluation_correction_archive is not None and evaluation_correction_directory is not None:
            archives.archive_and_move_directory(source_directory=evaluation_correction_directory,
                                                destination_directory=moodle_evaluation_correction_archive)

            return MoodleArchiveCompletedResponseDTO(source_file=evaluation_correction_directory,
                                                     destination_directory=moodle_evaluation_correction_archive)

        return MoodleArchiveCompletedResponseDTO(source_file=None,
                                                 destination_directory=None)


    def get_grade_reference_dto(self, course_id: int, evaluation_id: int) -> GradeReferencePlotDTO:
        active_student_ids = self._course_student_services.list_active_student_ids(course_id=course_id)

        return self._student_evaluation_services.get_grade_reference_plot_dto(evaluation_id=evaluation_id,
                                                                              active_student_ids=active_student_ids)

    def get_note_distribution_save_path(self, course_id: int, evaluation_id: int) -> Path:
        genote_directory = self._course_path_services.get_genote_directory(course_id=course_id)
        evaluation_title = self._evaluation_services.get_evaluation_title(evaluation_id=evaluation_id)

        return genote_directory / f"{evaluation_title} - Distribution des notes"

    @staticmethod
    def export_table_to_excel(grade_reference_plot_dto: GradeReferencePlotDTO, export_path: Path):
        dict_to_export = asdict(grade_reference_plot_dto)
        df = pd.DataFrame(dict_to_export)

        with pd.ExcelWriter(export_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Notes", index=False)
            worksheet = writer.sheets["Notes"]

            for col in worksheet.columns:
                cell_max_len = 0

                col_letter = col[0].column_letter
                for cell in col:
                    if cell.value is not None:
                        cell.alignment = cell.alignment.copy(horizontal="left", vertical="top", wrap_text=True)
                        cell_max_len = max(cell_max_len, len(str(cell.value)))

                worksheet.column_dimensions[col_letter].width = min(cell_max_len + 6, 50)

            for row_idx, row in enumerate(worksheet.iter_rows(min_row=2), start=2):
                max_lines = 1
                for cell in row:
                    if cell.value is not None:
                        col_width = worksheet.column_dimensions[cell.column_letter].width
                        text_length = len(str(cell.value))
                        if col_width > 3:
                            lines = (text_length // int(col_width - 3)) + 1
                            max_lines = max(max_lines, lines)

                worksheet.row_dimensions[row_idx].height = max(max_lines * 12, 20)

    def _load_genote_file_operations(self, course_id: int) -> GeNoteGradeFileOperations:
        genote_directory = self._course_path_services.get_genote_directory(course_id=course_id)
        genote_filename = self._course_services.get_genote_filename(course_id=course_id)
        genote_path = genote_directory / genote_filename

        return GeNoteGradeFileOperations(file_path=genote_path)