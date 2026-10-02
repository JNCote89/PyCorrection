from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.py_correction.database.base.base_model import BaseORM

if TYPE_CHECKING:
    from src.py_correction.database.student.models.student_orm import StudentORM
    from src.py_correction.database.evaluation.models.evaluation_orm import EvaluationORM
    from src.py_correction.database.reference.models.reference_orm import ReferenceORM


class StudentEvaluationORM(BaseORM):
    __tablename__ = "student_evaluations"

    # --- Keys ---
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    evaluation_id: Mapped[int] = mapped_column(ForeignKey("evaluations.id"), nullable=False)

    # --- Columns ---
    grade: Mapped[Decimal] = mapped_column(Numeric(precision=5, scale=2), nullable=True)

    # --- Relationships ---
    references: Mapped[list["ReferenceORM"]] = relationship("ReferenceORM",
                                                            back_populates="student_evaluation",
                                                            cascade="all, delete-orphan")
    student: Mapped["StudentORM"] = relationship("StudentORM", back_populates="student_evaluations")
    evaluation: Mapped["EvaluationORM"] = relationship("EvaluationORM", back_populates="student_evaluations")

    # --- Constraints ---
    __table_args__ = (UniqueConstraint("student_id", "evaluation_id", name="unique_student_evaluation"),)
