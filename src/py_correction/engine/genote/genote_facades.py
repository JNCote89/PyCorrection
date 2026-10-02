import logging
from pathlib import Path

from src.py_correction.core.domains.course.course_dtos import CourseCreateDTO
from src.py_correction.core.domains.evaluation.evaluation_dtos import EvaluationCreateDTO
from src.py_correction.core.domains.shared.shared_enums import ImportTypeEnum
from src.py_correction.core.domains.student.student_dtos import StudentCreateDTO
from src.py_correction.engine.genote.internal.genote_file_models import GeNoteGradeFileData
from src.py_correction.utils import date_format

logger = logging.getLogger(__name__)


class GeNoteGradeFileFacade:

    def __init__(self, file_path: Path):
        self._genote_grade_file = GeNoteGradeFileData(file_path=file_path)

    def get_course_create_dto(self) -> CourseCreateDTO:
        return CourseCreateDTO(semester=self._genote_grade_file.semester,
                               code=self._genote_grade_file.course_code,
                               name=self._genote_grade_file.course_name,
                               group=self._genote_grade_file.group,
                               genote_filename=self._genote_grade_file.filename,
                               creation_date=date_format.get_utc_now(),
                               import_type=ImportTypeEnum.GENOTE)

    def get_evaluation_create_dto(self) -> list[EvaluationCreateDTO]:
        return [EvaluationCreateDTO(title=evaluation_info.title,
                                    maximum_grade=evaluation_info.maximum_grade,
                                    import_type=ImportTypeEnum.GENOTE)
                for evaluation_info in self._genote_grade_file.evaluation_list]

    def get_student_create_dto(self) -> list[StudentCreateDTO]:
        return [StudentCreateDTO(cip=student.cip,
                                 first_name=student.first_name,
                                 last_name=student.last_name,
                                 import_type=ImportTypeEnum.GENOTE)
                for student in self._genote_grade_file.student_list]
