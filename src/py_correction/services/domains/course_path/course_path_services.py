import logging
from pathlib import Path
import shutil
from typing import TYPE_CHECKING

from src.py_correction.core.domains.course_path.course_path_dtos import (CoursePathCreateDTO,
                                                                         UpdateCoursePathDTO)
from src.py_correction.core.domains.evaluation.evaluation_dtos import EvaluationTemplateCompletedResponseDTO
from src.py_correction.database.course_path.course_path_CRUD import CoursePathCRUD
from src.py_correction.engine.excel.excel_operations import get_excel_paths_from_directory
from src.py_correction.services.domains.course_path.course_path_mappers import to_course_path_orm

if TYPE_CHECKING:
    from src.py_correction.core.event_bus import EventBus
    from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)


class CoursePathServices:

    def __init__(self, session_factory: "sessionmaker", event_bus: "EventBus"):
        self._session_factory = session_factory

        self._course_path_crud = CoursePathCRUD()

        self._event_bus = event_bus

    def add_course_path_from_dto(self, course_path_create_dto: CoursePathCreateDTO, course_id: int):
        course_path_orm = to_course_path_orm(dto=course_path_create_dto, course_id=course_id)
        with self._session_factory.begin() as session:
            session.add(course_path_orm)

    def scan_evaluation_template_paths_directory(self, course_id: int) -> list[Path] | None:
        course_path_correction_template = self._get_correction_template_directory(course_id=course_id)
        template_paths = get_excel_paths_from_directory(course_path_correction_template)
        return template_paths

    def check_if_template_file_exists(self, course_id: int, imported_file_path: Path) -> Path | None:
        imported_paths = self.scan_evaluation_template_paths_directory(course_id=course_id)

        if imported_paths is None:
            return None

        if isinstance(imported_paths, list):
            imported_filenames = [path.name for path in imported_paths]
            if imported_file_path.name in imported_filenames:
                return imported_file_path

        return None

    def import_evaluation_file_template(self, template_file_path: Path, course_id: int) -> None:
        course_path_correction_template = self._get_correction_template_directory(
            course_id=course_id)

        if course_path_correction_template:
            self._copy_evaluation_template_file_inside_directory(import_path=template_file_path,
                                                                 template_directory_path=course_path_correction_template)

    def get_submissions_directory(self, course_id: int) -> Path | None:
        with self._session_factory() as session:
            course_paths = self._course_path_crud.get_course_path_orm(session=session, course_id=course_id)
            return course_paths.submissions_directory if course_paths is not None else None

    def get_correction_directory(self, course_id: int) -> Path | None:
        with self._session_factory() as session:
            course_paths = self._course_path_crud.get_course_path_orm(session=session, course_id=course_id)
            return course_paths.corrections_directory if course_paths is not None else None

    def get_submission_archives_directory(self, course_id: int) -> Path | None:
        with self._session_factory() as session:
            course_paths = self._course_path_crud.get_course_path_orm(session, course_id=course_id)
            return course_paths.submission_archives_directory if course_paths is not None else None

    def get_correction_archives_directory(self, course_id: int) -> Path | None:
        with self._session_factory() as session:
            course_paths = self._course_path_crud.get_course_path_orm(session, course_id=course_id)
            return course_paths.correction_archives_directory if course_paths is not None else None

    def get_genote_directory(self, course_id: int):
        with self._session_factory() as session:
            course_paths = self._course_path_crud.get_course_path_orm(session, course_id=course_id)
            return course_paths.grades_directory if course_paths is not None else None

    def get_course_root_directory(self, course_id: int):
        with self._session_factory() as session:
            course_paths = self._course_path_crud.get_course_path_orm(session, course_id=course_id)
            return course_paths.course_root_path if course_paths is not None else None

    def update_course_path_from_dto(self, update_dto: UpdateCoursePathDTO):
        if update_dto.course_id:
            with self._session_factory.begin() as session:
                self._course_path_crud.update_course_path(session=session,
                                                          update_dto=update_dto)

    def _get_correction_template_directory(self, course_id: int) -> Path | None:
        with self._session_factory() as session:
            course_paths = self._course_path_crud.get_course_path_orm(session, course_id=course_id)
            return course_paths.correction_templates_directory if course_paths is not None else None

    def _copy_evaluation_template_file_inside_directory(self, import_path: Path, template_directory_path: Path) -> None:
        shutil.copy(import_path, template_directory_path)

        response_dto = EvaluationTemplateCompletedResponseDTO(original_path=import_path,
                                                              template_directory=template_directory_path)
        self._event_bus.evaluation.templateFileImportCompleted.emit(response_dto)