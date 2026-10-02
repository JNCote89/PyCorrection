from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class StudentInfo:
    cip: str
    first_name: str
    last_name: str
    is_active: bool = True


@dataclass(frozen=True, slots=True)
class EvaluationInfo:
    title: str
    maximum_grade: Decimal | None
