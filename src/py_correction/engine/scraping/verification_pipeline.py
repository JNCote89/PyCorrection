from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Protocol, override

from src.py_correction.core.domains.reference.reference_dtos import ReferenceTableDTO
from src.py_correction.core.domains.reference.reference_enums import (EvidenceLevelEnum, ReferenceTypeEnum,
                                                                      ReferenceVerificationStatusEnum)
from src.py_correction.engine.reference.parsers import crossref_parser
from src.py_correction.engine.scraping.internal import doi_verification, url_verification, verification_utils

logger = logging.getLogger(__name__)


@dataclass
class VerificationContextProtocol(Protocol):
    dto: ReferenceTableDTO
    is_halted: bool


@dataclass
class ScientificVerificationContext:
    dto: ReferenceTableDTO
    crossref_message: dict | None = None
    is_halted: bool = False


@dataclass
class URLVerificationContext:
    dto: ReferenceTableDTO
    url_title: str | None = None
    is_halted: bool = False


class BaseVerificationPipeline[TContext: VerificationContextProtocol](ABC):

    def __init__(self, reference_table_dto: ReferenceTableDTO):
        self._context = self.create_context(reference_table_dto)

    @abstractmethod
    def create_context(self, dto: ReferenceTableDTO) -> TContext:
        pass

    @abstractmethod
    def get_steps(self) -> list[Callable[[TContext], None]]:
        pass

    def execute(self) -> ReferenceTableDTO:
        for step in self.get_steps():
            step(self._context)
            if self._context.is_halted:
                break
        return self._context.dto

    @staticmethod
    def _check_verification_status(context: VerificationContextProtocol) -> None:
        if context.dto.verification_status is not None:
            context.is_halted = True

    @staticmethod
    def _check_has_url(context: VerificationContextProtocol) -> None:
        if not context.dto.url:
            context.dto.verification_status = ReferenceVerificationStatusEnum.TO_CHECK
            context.dto.cross_reference = "Cette référence n'a pas d'URL pour vérifier les métadonnées."
            context.is_halted = True


class ScientificReferenceVerificationPipeline(BaseVerificationPipeline[ScientificVerificationContext]):

    @override
    def create_context(self, dto: ReferenceTableDTO) -> ScientificVerificationContext:
        return ScientificVerificationContext(dto=dto)

    @override
    def get_steps(self) -> list[Callable[[ScientificVerificationContext], None]]:
        return [self._check_verification_status,
                self._check_has_url,
                self._retrieve_crossref_metadata,
                self._add_crossref_label,
                self._match_title,
                self._check_literature_type,
                self._check_evidence_level]

    @staticmethod
    def _retrieve_crossref_metadata(context: ScientificVerificationContext) -> None:
        assert context.dto.url is not None, "URL check should have halted pipeline if None"

        crossref_message = doi_verification.fetch_crossref_metadata(doi=context.dto.url)

        if not crossref_message:
            context.dto.verification_status = ReferenceVerificationStatusEnum.TO_CHECK
            context.dto.cross_reference = "Les métadonnées n'ont pas pu être vérifées sur CrossRef pour le DOI fournit."
            context.is_halted = True

        else:
            context.crossref_message = crossref_message

    @staticmethod
    def _add_crossref_label(context: ScientificVerificationContext) -> None:
        message = context.crossref_message or {}

        try:
            context.dto.cross_reference = crossref_parser.format_crossref_to_csl(crossref_message=message)
        except Exception as e:
            logger.debug(f"CSL formatting failed: {e}")

            titles = message.get("title")
            title = titles[0] if isinstance(titles, list) and titles else None

            # In case the pypandoc parser chocks on weird characters in the metadata
            if title:
                context.dto.cross_reference = f"Le titre de la référence fournie est : {title}"
            else:
                context.dto.cross_reference = "Le titre n'est pas disponible sur CrossRef."

    @staticmethod
    def _match_title(context: ScientificVerificationContext) -> None:
        message = context.crossref_message or {}
        titles = message.get("title")
        metadata_title = titles[0] if isinstance(titles, list) and titles else None

        is_title_matching = verification_utils.title_similarity(student_title=context.dto.title,
                                                                metadata_title=metadata_title)

        if not is_title_matching:
            context.dto.verification_status = ReferenceVerificationStatusEnum.TO_CHECK
            context.is_halted = True

        else:
            context.dto.verification_status = ReferenceVerificationStatusEnum.VALID

    @staticmethod
    def _check_literature_type(context: ScientificVerificationContext) -> None:
        assert context.dto.url is not None, "URL check should have halted pipeline if None"

        is_peer_reviewed = doi_verification.check_is_peer_reviewed(doi=context.dto.url)

        if not is_peer_reviewed:
            context.dto.peer_reviewed = False
            context.dto.reference_type = ReferenceTypeEnum.SCIENTIFIC_NO_REVIEW

        else:
            context.dto.peer_reviewed = True
            context.dto.reference_type = ReferenceTypeEnum.SCIENTIFIC_PEER_REVIEW

    @staticmethod
    def _check_evidence_level(context: ScientificVerificationContext) -> None:
        is_article_review = doi_verification.check_is_article_review(title=context.dto.title)

        if is_article_review and context.dto.peer_reviewed:
            context.dto.evidence_level = EvidenceLevelEnum.HIGH

        elif context.dto.peer_reviewed:
            context.dto.evidence_level = EvidenceLevelEnum.MODERATE

        else:
            context.dto.evidence_level = EvidenceLevelEnum.LOW


class URLReferenceVerificationPipeline(BaseVerificationPipeline[URLVerificationContext]):

    @override
    def create_context(self, dto: ReferenceTableDTO) -> URLVerificationContext:
        return URLVerificationContext(dto=dto)

    @override
    def get_steps(self) -> list[Callable[[URLVerificationContext], None]]:
        return [self._check_verification_status,
                self._check_has_url,
                self._retrieve_url_metadata,
                self._match_title]

    @staticmethod
    def _retrieve_url_metadata(context: URLVerificationContext) -> None:
        assert context.dto.url is not None, "URL check should have halted pipeline if None"

        title = url_verification.get_metadata_title(context.dto.url)
        context.url_title = title
        context.dto.cross_reference = title

        # Might flag false negative if the student provides a proxy URL to a scientific publication or do not use the
        # DOI.
        context.dto.reference_type = ReferenceTypeEnum.GREY
        context.dto.evidence_level = EvidenceLevelEnum.NO_EVIDENCE

    @staticmethod
    def _match_title(context: URLVerificationContext) -> None:

        is_title_matching = verification_utils.title_similarity(student_title=context.dto.title,
                                                                metadata_title=context.url_title)

        if not is_title_matching:
            context.dto.verification_status = ReferenceVerificationStatusEnum.TO_CHECK

        else:
            context.dto.verification_status = ReferenceVerificationStatusEnum.VALID
