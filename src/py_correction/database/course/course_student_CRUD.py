from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.py_correction.database.base.base_CRUD import BaseCRUD
from src.py_correction.database.course.models.course_student_orm import CourseStudentORM

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from src.py_correction.core.domains.course.course_student_dtos import CourseStudentUpdateDTO


class CourseStudentCRUD(BaseCRUD[CourseStudentORM]):
    model = CourseStudentORM

    def update_course_student(self, session: "Session", course_student_update_dto: "CourseStudentUpdateDTO"):
        stmt = select(self.model).where(self.model.course_id == course_student_update_dto.course_id,
                                        self.model.student_id == course_student_update_dto.student_id)
        db_record = session.scalars(stmt).first()
        if db_record:
            self._update_from_dto(db_record=db_record, update_dto=course_student_update_dto)

    def list_course_students_records(self, session: "Session", course_id: int) -> list[CourseStudentORM]:
        stmt = select(self.model).options(joinedload(self.model.student)).where(self.model.course_id == course_id)
        records = session.scalars(stmt).all()
        return list(records)

    def list_active_course_students_records(self, session: "Session", course_id: int) -> list[CourseStudentORM]:
        stmt = select(self.model).options(joinedload(self.model.student)
                                          ).where(self.model.course_id == course_id,
                                                  self.model.is_active == True)
        records = session.scalars(stmt).all()
        return list(records)
