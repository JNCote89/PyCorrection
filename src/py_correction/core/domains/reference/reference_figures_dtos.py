from dataclasses import dataclass
from typing import Any

from src.py_correction.core.domains.reference.reference_enums import EvidenceLevelEnum, ReferenceTypeEnum

LIGHT_GREEN = "#07dd05"
GREEN = "#0e5913"
YELLOW = "#DA9E38"
RED = "#990B0B"
GREY = "#AAAAAA"

PIE_CHART_COLOR_SCHEME = {EvidenceLevelEnum.HIGH: LIGHT_GREEN,
                          EvidenceLevelEnum.MODERATE: GREEN,
                          EvidenceLevelEnum.LOW: YELLOW,
                          EvidenceLevelEnum.VERY_LOW: RED,
                          EvidenceLevelEnum.NO_EVIDENCE: GREY}

BAR_CHART_COLOR_SCHEME = {ReferenceTypeEnum.GREY: GREY,
                          ReferenceTypeEnum.SCIENTIFIC_NO_REVIEW: YELLOW,
                          ReferenceTypeEnum.SCIENTIFIC_PEER_REVIEW: LIGHT_GREEN}


@dataclass
class EvidenceLevelPieChartDTO:
    high_count: int | None = 0
    moderate_count: int | None = 0
    low_count: int | None = 0
    very_low_count: int | None = 0
    no_evidence_count: int | None = 0

    def __post_init__(self):
        self.high_count = self.high_count or 0
        self.moderate_count = self.moderate_count or 0
        self.low_count = self.low_count or 0
        self.very_low_count = self.very_low_count or 0
        self.no_evidence_count = self.no_evidence_count or 0

    @property
    def _active_items(self) -> list[tuple[int | None, EvidenceLevelEnum, str]]:
        raw_data = [
            (self.high_count, EvidenceLevelEnum.HIGH, PIE_CHART_COLOR_SCHEME[EvidenceLevelEnum.HIGH]),
            (self.moderate_count, EvidenceLevelEnum.MODERATE, PIE_CHART_COLOR_SCHEME[EvidenceLevelEnum.MODERATE]),
            (self.low_count, EvidenceLevelEnum.LOW, PIE_CHART_COLOR_SCHEME[EvidenceLevelEnum.LOW]),
            (self.very_low_count, EvidenceLevelEnum.VERY_LOW, PIE_CHART_COLOR_SCHEME[EvidenceLevelEnum.VERY_LOW]),
            (self.no_evidence_count, EvidenceLevelEnum.NO_EVIDENCE,
             PIE_CHART_COLOR_SCHEME[EvidenceLevelEnum.NO_EVIDENCE])]

        return [item for item in raw_data if item[0] > 0]

    @property
    def values(self) -> list[int | None] | list[Any]:
        items = self._active_items
        return [item[0] for item in items] if items else []

    @property
    def labels(self) -> list[str]:
        items = self._active_items
        return [f"{item[1]}\n(n={item[0]})" for item in items] if items else []

    @property
    def colors(self) -> list[str]:
        items = self._active_items
        return [item[2] for item in items] if items else []


@dataclass
class ReferenceTypeStackedBarChartDTO:
    bins: list[str]
    grey_counts: list[int]
    scientific_no_review_counts: list[int]
    scientific_review_counts: list[int]

    color_scheme = BAR_CHART_COLOR_SCHEME

    @property
    def grey_label(self) -> str:
        return ReferenceTypeEnum.GREY

    @property
    def scientific_no_review_label(self) -> str:
        return ReferenceTypeEnum.SCIENTIFIC_NO_REVIEW

    @property
    def scientific_review_label(self) -> str:
        return ReferenceTypeEnum.SCIENTIFIC_PEER_REVIEW


@dataclass
class GradeReferencePlotDTO:
    bins: list[str]
    grades: list[float]
    grey_counts: list[int]
    scientific_no_review_counts: list[int]
    scientific_review_counts: list[int]

    color_scheme = BAR_CHART_COLOR_SCHEME

    @property
    def grey_label(self) -> str:
        return ReferenceTypeEnum.GREY

    @property
    def scientific_no_review_label(self) -> str:
        return ReferenceTypeEnum.SCIENTIFIC_NO_REVIEW

    @property
    def scientific_review_label(self) -> str:
        return ReferenceTypeEnum.SCIENTIFIC_PEER_REVIEW

    @property
    def grade_label(self) -> str:
        return "Note"
