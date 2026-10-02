from typing import TYPE_CHECKING

from src.py_correction.core.domains.course.course_student_dtos import CourseStudentTableDTO, CourseStudentUpdateDTO
from src.py_correction.core.domains.shared.shared_dtos import SelectionWidgetDTO
from src.py_correction.database.course.course_student_CRUD import CourseStudentCRUD
from src.py_correction.services.domains.course import course_student_mappers

if TYPE_CHECKING:
    from sqlalchemy.orm import sessionmaker
    from src.py_correction.core.event_bus import EventBus


class CourseStudentServices:

    def __init__(self, session_factory: "sessionmaker", event_bus: "EventBus"):
        self._session_factory = session_factory

        self._course_student_crud = CourseStudentCRUD()

        self._event_bus = event_bus

    def update_course_student(self, course_student_update_dto: CourseStudentUpdateDTO) -> None:
        if course_student_update_dto.student_id:
            with self._session_factory.begin() as session:
                self._course_student_crud.update_course_student(session=session,
                                                                course_student_update_dto=course_student_update_dto)

    def list_course_student_rows(self, course_id: int) -> list[CourseStudentTableDTO]:
        with self._session_factory() as session:
            course_student_orm_records = self._course_student_crud.list_course_students_records(session=session,
                                                                                                course_id=course_id)
            return [course_student_mappers.to_course_student_table_dto(course_student_orm=record)
                    for record in course_student_orm_records]

    def list_active_student_records(self, course_id: int) -> list[SelectionWidgetDTO]:
        with self._session_factory() as session:
            course_student_orm_records = self._course_student_crud.list_active_course_students_records(session=session,
                                                                                                       course_id=course_id)
            return [course_student_mappers.to_course_student_selection_dto(course_student_orm=record)
                    for record in course_student_orm_records]

    def list_active_student_ids(self, course_id: int) -> list[int]:
        with self._session_factory() as session:
            course_student_orm_records = self._course_student_crud.list_active_course_students_records(session=session,
                                                                                                       course_id=course_id)
            return [course_student_orm_record.id for course_student_orm_record in course_student_orm_records]
