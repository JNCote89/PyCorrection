from dataclasses import dataclass, field, fields
from enum import StrEnum
from typing import Any

from src.py_correction.core.domains.shared.shared_enums import UNSET


@dataclass
class ReferenceTableDTO:
    # To easily import delegates inside the table and export data.
    class Fields(StrEnum):
        STUDENT_REFERENCE_HTML = "student_reference_html"
        STUDENT_REFERENCE = "student_reference"
        CROSS_REFERENCE = "cross_reference"
        VERIFICATION_STATUS = "verification_status"
        RELEVANCE = "relevance"
        REFERENCE_TYPE = "reference_type"
        EVIDENCE_LEVEL = "evidence_level"
        YEAR = "year"

    # For table row identification/ dry run check
    reference_id: int | None = field(metadata={"visible": False})
    student_reference: str = field(metadata={"visible": False})
    url: str | None = field(metadata={"visible": False})
    title: str | None = field(metadata={"visible": False})
    peer_reviewed: bool | None = field(default=False, metadata={"visible": False})

    # For table columns
    student_reference_html: str | None = field(default=None, metadata={"label": "Référence dans le travail",
                                                                       "visible": True})
    cross_reference: str | None = field(default=None, metadata={"label": "Métadonnées de l'URL/DOI", "visible": True})
    verification_status: str | None = field(default=None, metadata={"label": "Vérification", "visible": True})
    relevance: str | None = field(default=None,
                                  metadata={"label": "Pertinence et alignement avec le texte", "visible": True})
    reference_type: str | None = field(default=None, metadata={"label": "Type de littérature", "visible": True})
    evidence_level: str | None = field(default=None, metadata={"label": "Niveau de preuve", "visible": True})
    year: int | None = field(default=None, metadata={"label": "Année de la référence dans le travail", "visible": True})

    @classmethod
    def get_headers(cls) -> list[str]:
        return [f.metadata["label"] for f in fields(cls) if f.metadata["visible"] is True]

    @classmethod
    def get_field_names(cls) -> list[str]:
        return [f.name for f in fields(cls) if f.metadata["visible"] is True]


@dataclass
class ReferenceUpdateDTO:
    reference_id: int | None = field(metadata={"updatable": False})
    student_reference: str | None = field(default=None, metadata={"updatable": False})
    student_reference_html: str | None = field(default=None, metadata={"updatable": False})
    url: str | None = field(default=None, metadata={"updatable": False})
    title: str | None = field(default=None, metadata={"updatable": False})

    cross_reference: str | None = field(default=UNSET, metadata={"updatable": True})
    verification_status: str | None = field(default=UNSET, metadata={"updatable": True})
    relevance: str | None = field(default=UNSET, metadata={"updatable": True})
    reference_type: str = field(default=UNSET, metadata={"updatable": True})
    evidence_level: str | None = field(default=UNSET, metadata={"updatable": True})
    year: int | None = field(default=UNSET, metadata={"updatable": True})
    peer_reviewed: bool = field(default=UNSET, metadata={"updatable": True})

    def updatable_items_to_dict(self) -> dict:
        updatable_fields = [f.name for f in fields(self) if f.metadata["updatable"] is not False]
        return {k: v for k, v in self.__dict__.items() if k in updatable_fields and v is not UNSET}

    @classmethod
    def from_table_dto(cls, table_dto: ReferenceTableDTO) -> "ReferenceUpdateDTO":
        kwargs: dict[str, Any] = {}

        for f in fields(cls):
            if hasattr(table_dto, f.name):
                val = getattr(table_dto, f.name)
                if val is not None or f.metadata.get("updatable") is False:
                    kwargs[f.name] = val

        return cls(**kwargs) # type: ignore[arg-type]


@dataclass
class ReferenceSubmissionsDTO:
    references: list[str] = field(default_factory=list)
    excluded_evaluation_ids: list[int] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class DryRunWarningResponseDTO:
    course_id: int | None
    evaluation_id: int | None
    student_id: int | None
