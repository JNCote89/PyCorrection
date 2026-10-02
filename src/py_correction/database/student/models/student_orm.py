from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.py_correction.database.base.base_model import BaseORM

if TYPE_CHECKING:
    from src.py_correction.database.student.models.student_evaluation_orm import StudentEvaluationORM
    from src.py_correction.database.course.models.course_student_orm import CourseStudentORM


class StudentORM(BaseORM):
    __tablename__ = "students"

    # --- Keys ---
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # --- Columns ---
    cip: Mapped[str] = mapped_column(String(8), unique=True, nullable=False)
    last_name: Mapped[str] = mapped_column(String(128), nullable=False)
    first_name: Mapped[str] = mapped_column(String(128), nullable=False)

    # --- Relationships ---
    student_evaluations: Mapped[list["StudentEvaluationORM"]] = relationship("StudentEvaluationORM",
                                                                             back_populates="student",
                                                                             cascade="all, delete-orphan")
    course_students: Mapped[list["CourseStudentORM"]] = relationship("CourseStudentORM", back_populates="student",
                                                                     cascade="all, delete-orphan")
