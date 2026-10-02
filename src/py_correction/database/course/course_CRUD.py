from typing import TYPE_CHECKING

from sqlalchemy import select

from src.py_correction.database.base.base_CRUD import BaseCRUD
from src.py_correction.database.course.models.course_orm import CourseORM

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class CourseCRUD(BaseCRUD[CourseORM]):
    model = CourseORM

    def list_course_records_by_date(self, session: "Session") -> list[CourseORM]:
        stmt = select(self.model).order_by(self.model.creation_date)
        records = session.scalars(stmt).all()
        return [row for row in records]
