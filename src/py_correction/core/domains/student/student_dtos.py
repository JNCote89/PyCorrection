from dataclasses import dataclass

from src.py_correction.core.domains.shared.shared_enums import ImportTypeEnum


@dataclass(frozen=True, slots=True)
class StudentCreateDTO:
    cip: str
    last_name: str
    first_name: str
    import_type: ImportTypeEnum

