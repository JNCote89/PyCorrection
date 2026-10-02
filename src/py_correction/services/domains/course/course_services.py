from dataclasses import dataclass
from datetime import datetime
import logging
from typing import TYPE_CHECKING

from sqlalchemy.exc import IntegrityError

from src.py_correction.core import nuitka_helpers
from src.py_correction.core.domains.course.course_dtos import (CourseCreateDTO, CourseResponseDTO,
                                                               CourseSelectionWidgetDTO,
                                                               CourseTableDTO)
from src.py_correction.core.exceptions import DatabaseError
from src.py_correction.database.course.course_CRUD import CourseCRUD
from src.py_correction.database.course.models.course_orm import CourseORM
from src.py_correction.database.evaluation.models.evaluation_orm import EvaluationORM
from src.py_correction.services.domains.course import course_mappers

if TYPE_CHECKING:
    from sqlalchemy.orm import sessionmaker
    from src.py_correction.core.event_bus import EventBus

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class _CacheCourse:
    id: int
    semester: str
    code: str
    name: str
    group: str
    genote_filename: str
    import_type: str
    creation_date: str | datetime

    @classmethod
    def from_course_orm(cls, course_orm: CourseORM):
        return cls(id=course_orm.id,
                   semester=course_orm.semester,
                   code=course_orm.code,
                   name=course_orm.name,
                   group=course_orm.group,
                   genote_filename=course_orm.genote_filename,
                   import_type=course_orm.import_type,
                   creation_date=course_orm.creation_date)


class CourseServices:

    def __init__(self, session_factory: "sessionmaker", event_bus: "EventBus"):
        self._session_factory = session_factory

        self._course_CRUD = CourseCRUD()
        self._event_bus = event_bus

        self._cache_course_selection_dtos: list[CourseSelectionWidgetDTO] | None = None
        self._cache_courses: dict[int, _CacheCourse] = {}

        self._connect_upstream_signals()

    def _connect_upstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._event_bus.database.courseArchived,
                                    slot=self._remove_course_caches)
        nuitka_helpers.safe_connect(signal=self._event_bus.database.courseRestored,
                                    slot=self._load_course_selection_dtos)

    def check_valid_data(self) -> None:
        has_data = bool(self.list_course_selection_dtos())
        self._event_bus.database.courseHasValidData.emit(has_data)

    def add_course_from_dto(self, course_create_dto: CourseCreateDTO) -> CourseResponseDTO:
        course_orm = course_mappers.to_course_orm(course_input_dto=course_create_dto)
        try:
            with self._session_factory.begin() as session:
                session.add(course_orm)
                session.flush()
                response_dto = course_mappers.to_course_response_dto(course_orm=course_orm)

            self._load_course_selection_dtos()
            self._event_bus.course.newCourseIDImported.emit(response_dto.id)
            self._event_bus.course.dataChanged.emit()
            return response_dto

        except IntegrityError as e:
            self._event_bus.database.courseIntegrityFailed.emit(course_create_dto)
            logger.warning(e)
            raise DatabaseError()

    def list_course_table_rows(self) -> list[CourseTableDTO]:
        with self._session_factory() as session:
            courses_orm_records = self._course_CRUD.list_course_records_by_date(session=session)
            return [course_mappers.to_course_table_dto(record) for record in courses_orm_records]

    def list_course_selection_dtos(self) -> list[CourseSelectionWidgetDTO]:
        if self._cache_course_selection_dtos is None:
            self._load_course_selection_dtos()

        return list(self._cache_course_selection_dtos) # type: ignore

    def get_course_evaluations(self, course_id: int) -> list[EvaluationORM]:
        with self._session_factory() as session:
            course = self._course_CRUD.get_by_id(session=session, record_id=course_id)
            return course.evaluations if course is not None else []

    def get_course(self, course_id: int) -> _CacheCourse | None:
        course = self._get_course_from_cache(course_id)
        if course is not None:
            return course

        return self._load_course_into_cache(course_id)

    def get_genote_filename(self, course_id: int) -> str | None:
        course = self.get_course(course_id)
        return course.genote_filename if course else None

    def get_course_archive_name(self, course_id: int) -> str | None:
        course = self.get_course(course_id)
        return f"{course.code}_gr{course.group}_{course.semester}" if course is not None else None

    def _remove_course_caches(self, course_id: int) -> None:
        self._load_course_selection_dtos()
        self._cache_courses.pop(course_id, None)

    def _load_course_selection_dtos(self) -> None:
        with self._session_factory() as session:
            course_orm_records = self._course_CRUD.list_course_records_by_date(session=session)
            self._cache_course_selection_dtos = [course_mappers.to_course_selection_dto(course_orm=record)
                                                 for record in course_orm_records]

    def _get_course_from_cache(self, course_id: int) -> _CacheCourse | None:
        return self._cache_courses.get(course_id)

    def _load_course_into_cache(self, course_id: int) -> _CacheCourse | None:
        course = self._fetch_course_from_db(course_id)
        if course is not None:
            self._cache_courses[course.id] = course
        return course

    def _fetch_course_from_db(self, course_id: int) -> _CacheCourse | None:
        with self._session_factory() as session:
            course_orm = self._course_CRUD.get_by_id(session=session, record_id=course_id)
            return _CacheCourse.from_course_orm(course_orm) if course_orm else None


