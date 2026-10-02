from typing import TYPE_CHECKING

from sqlalchemy import select

from src.py_correction.database.base.base_CRUD import BaseCRUD
from src.py_correction.database.course_path.models.course_path_orm import CoursePathORM

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from src.py_correction.core.domains.course_path.course_path_dtos import UpdateCoursePathDTO

class CoursePathCRUD(BaseCRUD[CoursePathORM]):
    model = CoursePathORM

    def get_course_path_orm(self, session: "Session", course_id: int) -> CoursePathORM | None:
        stmt = select(self.model).where(self.model.course_id == course_id)
        return session.scalar(stmt)

    def update_course_path(self, session: "Session", update_dto: "UpdateCoursePathDTO"):
        stmt = select(self.model).where(self.model.course_id == update_dto.course_id,
                                        self.model.id == update_dto.id)
        db_record = session.scalars(stmt).first()
        if db_record:
            self._update_from_dto(db_record=db_record, update_dto=update_dto)
