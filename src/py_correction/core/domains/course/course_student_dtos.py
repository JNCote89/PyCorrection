from dataclasses import dataclass, field, fields
from enum import StrEnum

from src.py_correction.core.domains.shared.shared_enums import ImportTypeEnum, UNSET


@dataclass(slots=True)
class CourseStudentTableDTO:
    # To easily check the field name inside the GUI to retrieve the activity status
    class Fields(StrEnum):
        IS_ACTIVE = "is_active"
        LAST_NAME = "last_name"

    student_id: int = field(metadata={"visible": False})
    course_id: int = field(metadata={"visible": False})
    cip: str = field(metadata={"label": "CIP", "visible": True})
    last_name: str = field(metadata={"label": "Nom de famille", "visible": True})
    first_name: str = field(metadata={"label": "Prénom", "visible": True})
    import_type: ImportTypeEnum = field(metadata={"label": "Type d'importation", "visible": True})
    is_active: bool = field(metadata={"label": "Actif/Inactif", "visible": True})

    @classmethod
    def get_headers(cls) -> list[str]:
        return [f.metadata["label"] for f in fields(cls) if f.metadata["visible"] is True]

    @classmethod
    def get_field_names(cls) -> list[str]:
        return [f.name for f in fields(cls) if f.metadata["visible"] is True]


@dataclass
class CourseStudentUpdateDTO:
    course_id: int = field(metadata={"updatable": False})
    student_id: int = field(metadata={"updatable": False})
    # At the moment, to avoid disconnection with GeNote, update are only allowed on the student status
    is_active: bool | object = field(default=UNSET, metadata={"updatable": True})

    def updatable_items_to_dict(self) -> dict:
        updatable_fields = [f.name for f in fields(self) if f.metadata["updatable"] is not False]
        return {k: v for k, v in self.__dict__.items() if k in updatable_fields and v is not UNSET}
