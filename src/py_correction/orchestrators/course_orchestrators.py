import logging
from pathlib import Path
from typing import TYPE_CHECKING

from src.py_correction.core.domains.course.course_dtos import CourseCreateDTO, CourseResponseDTO
from src.py_correction.core.domains.course_path.course_path_dtos import (CoursePathCreateDTO,
                                                                         GeNoteResponseDTO)
from src.py_correction.core.domains.evaluation.evaluation_dtos import EvaluationCreateDTO
from src.py_correction.core.domains.student.student_dtos import StudentCreateDTO
from src.py_correction.core.event_bus import EventBus
from src.py_correction.core.exceptions import DatabaseError
from src.py_correction.engine.genote.genote_facades import GeNoteGradeFileFacade
from src.py_correction.io_operations.filesystem import copy_and_rename_source, make_directories

if TYPE_CHECKING:
    from src.py_correction.core.settings_manager import SettingsManager
    from src.py_correction.services.domains.course.course_services import CourseServices
    from src.py_correction.services.domains.course_path.course_path_services import CoursePathServices
    from src.py_correction.services.domains.evaluation.evaluation_services import EvaluationServices
    from src.py_correction.services.domains.student.student_services import StudentServices

logger = logging.getLogger(__name__)


class BaseCourseOrchestrator:

    def __init__(self, course_path_services: "CoursePathServices", settings_manager: "SettingsManager"):
        self._course_path_services = course_path_services

        self._settings_manager = settings_manager

    def _add_course_path(self, course_response_dto: CourseResponseDTO) -> CoursePathCreateDTO:
        create_dto = CoursePathCreateDTO(
            user_root_directory=self._settings_manager.restored_settings.user_root_directory,
            semester=course_response_dto.semester,
            course_code=course_response_dto.code,
            group=course_response_dto.group)

        self._course_path_services.add_course_path_from_dto(course_path_create_dto=create_dto,
                                                            course_id=course_response_dto.id)
        return create_dto


class GeNoteOrchestrator(BaseCourseOrchestrator):
    def __init__(self, course_services: "CourseServices", student_services: "StudentServices",
                 evaluation_services: "EvaluationServices", course_path_services: "CoursePathServices",
                 settings_manager: "SettingsManager",
                 event_bus: "EventBus"):
        super().__init__(course_path_services=course_path_services, settings_manager=settings_manager)
        self._course_services = course_services
        self._student_services = student_services
        self._evaluation_services = evaluation_services
        self._event_bus = event_bus

    def import_genote_grade_file(self, file_path: Path) -> None:
        genote_file_data = GeNoteGradeFileFacade(file_path=file_path)

        course_create_dto = genote_file_data.get_course_create_dto()
        evaluation_create_dtos = genote_file_data.get_evaluation_create_dto()
        student_create_dtos = genote_file_data.get_student_create_dto()

        try:
            course_response_dto = self._course_services.add_course_from_dto(course_create_dto=course_create_dto)
            course_path_response_dto = self._add_course_path(course_response_dto=course_response_dto)
            self._add_evaluations(evaluation_create_dtos=evaluation_create_dtos, course_id=course_response_dto.id)
            self._add_students(student_create_dtos=student_create_dtos, course_id=course_response_dto.id)

            make_directories(course_path_response_dto.directories)

            new_source_path = copy_and_rename_source(file_path=Path(file_path),
                                                     destination_path=course_path_response_dto.grades_directory)

            genote_response_dto = GeNoteResponseDTO(new_source_path=new_source_path,
                                                    grade_directory_path=course_path_response_dto.grades_directory)

            self._event_bus.course.geNoteImportCompleted.emit(genote_response_dto)

        except DatabaseError:
            # Error handling and logging is done at the service level
            pass

        except Exception as e:
            # If a file exception happens
            logger.warning(e)

    def _add_evaluations(self, evaluation_create_dtos: list[EvaluationCreateDTO], course_id: int) -> None:
        self._evaluation_services.add_evaluation_from_dtos(evaluation_create_dtos=evaluation_create_dtos,
                                                           course_id=course_id)

    def _add_students(self, student_create_dtos: list[StudentCreateDTO], course_id: int) -> None:
        self._student_services.add_student_from_dtos(student_create_dtos=student_create_dtos,
                                                     course_id=course_id)


class CourseFormOrchestrator(BaseCourseOrchestrator):
    pass

    def __init__(self, course_services: "CourseServices", course_path_services: "CoursePathServices",
                 settings_manager: "SettingsManager",
                 event_bus: EventBus):
        super().__init__(course_path_services=course_path_services, settings_manager=settings_manager)
        self._course_services = course_services

        self._event_bus = event_bus

    def import_course_form(self, course_input_dto: CourseCreateDTO) -> None:
        try:
            course_response_dto = self._course_services.add_course_from_dto(course_create_dto=course_input_dto)
            course_path_response_dto = self._add_course_path(course_response_dto=course_response_dto)

            make_directories(directories=course_path_response_dto.directories)

            self._event_bus.course.formImportCompleted.emit(course_response_dto)

        except DatabaseError:
            # Error handling and logging is done at the service level
            pass

        except Exception as e:
            # If a file exception happens
            logger.warning(e)
