from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path


@dataclass(frozen=True, slots=True)
class MoodleArchiveCompletedResponseDTO:
    source_file: Path | None
    destination_directory: Path | None


@dataclass(frozen=True, slots=True)
class GeNoteUpdateFailedResponseDTO:
    failed_operations: list[str] | None
    evaluation_title: str


@dataclass(frozen=True, slots=True)
class UpdateGradeDTO:
    evaluation_id: int
    first_name: str
    last_name: str
    grade: Decimal | None


@dataclass(frozen=True, slots=True)
class GeNoteTransactionDTO:
    student_name: str
    student_grade: Decimal | None
    evaluation_title: str