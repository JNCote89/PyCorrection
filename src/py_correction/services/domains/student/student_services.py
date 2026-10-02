from typing import TYPE_CHECKING

from src.py_correction.core.domains.student.student_dtos import StudentCreateDTO
from src.py_correction.database.student.student_CRUD import StudentCRUD
from src.py_correction.services.domains.student.student_mappers import to_student_orm

if TYPE_CHECKING:
    from sqlalchemy.orm import sessionmaker
    from src.py_correction.core.event_bus import EventBus


class StudentServices:

    def __init__(self, session_factory: "sessionmaker", event_bus: "EventBus"):
        self._session_factory = session_factory
        self._student_CRUD = StudentCRUD()

        self._event_bus = event_bus

    def add_student_from_dto(self, student_create_dto: StudentCreateDTO, course_id: int) -> None:
        student_orm_model = to_student_orm(student_input_dto=student_create_dto)
        with self._session_factory.begin() as session:
            self._student_CRUD.upsert_student_course(session=session, student_orm_model=student_orm_model,
                                                     import_type=student_create_dto.import_type, course_id=course_id)
        self._event_bus.student.dataChanged.emit()

    def add_student_from_dtos(self, student_create_dtos: list[StudentCreateDTO], course_id: int) -> None:
        # To avoid emitting a signal after every student upsert on batch imports
        for student_create_dto in student_create_dtos:
            student_orm_model = to_student_orm(student_input_dto=student_create_dto)

            with self._session_factory.begin() as session:
                self._student_CRUD.upsert_student_course(session=session, student_orm_model=student_orm_model,
                                                         import_type=student_create_dto.import_type,
                                                         course_id=course_id)
        self._event_bus.student.dataChanged.emit()

    def get_student_full_name(self, student_id: int) -> str | None:
        with self._session_factory() as session:
            student = self._student_CRUD.get_by_id(session=session, record_id=student_id)
            return f"{student.last_name}, {student.first_name}" if student is not None else None
