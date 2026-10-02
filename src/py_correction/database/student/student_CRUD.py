from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.py_correction.database.base.base_CRUD import BaseCRUD
from src.py_correction.database.course.models.course_student_orm import CourseStudentORM
from src.py_correction.database.student.models.student_orm import StudentORM

if TYPE_CHECKING:
    from src.py_correction.core.domains.shared.shared_enums import ImportTypeEnum


class StudentCRUD(BaseCRUD[StudentORM]):
    model = StudentORM

    def _check_existing_student(self, session: Session, student_orm_model: StudentORM) -> StudentORM | None:
        stmt = select(self.model).options(selectinload(self.model.course_students)
                                          ).where(self.model.cip == student_orm_model.cip)
        return session.scalars(stmt).first()

    def upsert_student_course(self, session: Session, student_orm_model: StudentORM, course_id: int,
                              import_type: "ImportTypeEnum") -> None:
        existing_student = self._check_existing_student(session=session, student_orm_model=student_orm_model)

        if existing_student:
            existing_link = next((course_student for course_student in existing_student.course_students
                                  if course_student.course_id == course_id), None)
            if existing_link:
                return
            else:
                course_student_model = CourseStudentORM(import_type=import_type, course_id=course_id, # type: ignore[call-arg]
                                                        student_id=existing_student.id) # type: ignore[call-arg]
                existing_student.course_students.append(course_student_model)
        else:
            session.add(student_orm_model)
            session.flush()
            course_student_model = CourseStudentORM(import_type=import_type, course_id=course_id, # type: ignore[call-arg]
                                                    student_id=student_orm_model.id) # type: ignore[call-arg]
            student_orm_model.course_students.append(course_student_model)
