from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.py_correction.core.domains.shared.shared_enums import ImportTypeEnum
from src.py_correction.database.base.base_model import BaseORM

if TYPE_CHECKING:
    from src.py_correction.database.student.models.student_orm import StudentORM
    from src.py_correction.database.course.models.course_orm import CourseORM


class CourseStudentORM(BaseORM):
    __tablename__ = "course_students"

    # --- Keys ---
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))

    # --- Columns ---
    import_type: Mapped["ImportTypeEnum"] = mapped_column(String(64), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # --- Relationships ---
    student: Mapped["StudentORM"] = relationship("StudentORM", back_populates="course_students")
    course: Mapped["CourseORM"] = relationship("CourseORM", back_populates="course_students")

    # --- Constraints ---
    __table_args__ = (UniqueConstraint("course_id", "student_id", name="unique_course_student"),)
