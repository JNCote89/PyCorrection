from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.py_correction.database.base.base_model import BaseORM

if TYPE_CHECKING:
    from src.py_correction.database.student.models.student_evaluation_orm import StudentEvaluationORM


class ReferenceORM(BaseORM):
    __tablename__ = "references"

    # --- Keys ---
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_evaluation_id: Mapped[int] = mapped_column(ForeignKey("student_evaluations.id"), nullable=False)

    # --- Columns ---
    student_reference: Mapped[str] = mapped_column(String(1024), nullable=False)
    student_reference_html: Mapped[str] = mapped_column(String(1536), nullable=False)
    cross_reference: Mapped[str | None] = mapped_column(String(1024), default=None, nullable=True)
    verification_status: Mapped[str | None] = mapped_column(String(128), default=None, nullable=True)
    relevance: Mapped[str | None] = mapped_column(String(128), default=None, nullable=True)
    reference_type: Mapped[str | None] = mapped_column(String(128), default=None, nullable=True)
    evidence_level: Mapped[str | None] = mapped_column(String(128), default=None, nullable=True)
    year: Mapped[int | None] = mapped_column(SmallInteger, default=None, nullable=True)
    url: Mapped[str | None] = mapped_column(String(512), default=None, nullable=True)
    title: Mapped[str | None] = mapped_column(String(256), default=None, nullable=True)
    peer_reviewed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)

    # --- Relationships ---
    student_evaluation: Mapped["StudentEvaluationORM"] = relationship(back_populates="references")
