from src.py_correction.core.domains.reference.reference_dtos import (ReferenceTableDTO, ReferenceUpdateDTO)
from src.py_correction.database.reference.models.reference_orm import ReferenceORM


def to_reference_orm_foreign_key(student_evaluation_id: int, reference_table_dto: ReferenceTableDTO) -> ReferenceORM:
    return ReferenceORM(student_evaluation_id=student_evaluation_id,  # type: ignore
                        student_reference=reference_table_dto.student_reference,  # type: ignore
                        student_reference_html=reference_table_dto.student_reference_html,  # type: ignore
                        cross_reference=reference_table_dto.cross_reference,  # type: ignore
                        verification_status=reference_table_dto.verification_status,  # type: ignore
                        relevance=reference_table_dto.relevance,  # type: ignore
                        reference_type=reference_table_dto.reference_type,  # type: ignore
                        evidence_level=reference_table_dto.evidence_level,  # type: ignore
                        year=reference_table_dto.year,  # type: ignore
                        url=reference_table_dto.url,  # type: ignore
                        title=reference_table_dto.title,  # type: ignore
                        peer_reviewed=reference_table_dto.peer_reviewed)  # type: ignore


def to_reference_update_dto(reference_orm: ReferenceORM) -> ReferenceUpdateDTO:
    return ReferenceUpdateDTO(reference_id=reference_orm.id,
                              student_reference_html=reference_orm.student_reference_html,
                              student_reference=reference_orm.student_reference,
                              cross_reference=reference_orm.cross_reference,
                              verification_status=reference_orm.verification_status,
                              relevance=reference_orm.relevance,
                              evidence_level=reference_orm.evidence_level,
                              year=reference_orm.year,
                              url=reference_orm.url,
                              title=reference_orm.title,
                              peer_reviewed=reference_orm.peer_reviewed)


def to_reference_table_dto(reference_orm: ReferenceORM) -> ReferenceTableDTO:
    return ReferenceTableDTO(reference_id=reference_orm.id,
                             student_reference=reference_orm.student_reference,
                             student_reference_html=reference_orm.student_reference_html,
                             cross_reference=reference_orm.cross_reference,
                             verification_status=reference_orm.verification_status,
                             relevance=reference_orm.relevance,
                             reference_type=reference_orm.reference_type,
                             evidence_level=reference_orm.evidence_level,
                             year=reference_orm.year,
                             url=reference_orm.url,
                             title=reference_orm.title,
                             peer_reviewed=reference_orm.peer_reviewed)
