from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 1000)
pd.set_option('display.width', 2500)
pd.set_option('display.max_colwidth', 800)

from src.py_correction.core.domains.reference.reference_dtos import (ReferenceUpdateDTO, ReferenceTableDTO)
from src.py_correction.core.domains.reference.reference_figures_dtos import (ReferenceTypeStackedBarChartDTO,
                                                                         EvidenceLevelPieChartDTO)
from src.py_correction.core.domains.reference.reference_enums import (EvidenceLevelEnum, ReferenceVerificationStatusEnum,
                                                                  RelevanceLevelEnum, ReferenceTypeEnum)
from src.py_correction.database.reference.reference_CRUD import ReferenceCRUD
from src.py_correction.services.domains.reference.reference_mappers import (to_reference_orm_foreign_key, to_reference_table_dto)

if TYPE_CHECKING:
    from sqlalchemy.orm import sessionmaker
    from src.py_correction.core.event_bus import EventBus


class ReferenceServices:

    def __init__(self, session_factory: "sessionmaker", event_bus: "EventBus"):
        self._session_factory = session_factory

        self._reference_CRUD = ReferenceCRUD()

        self._event_bus = event_bus

    def bulk_insert_references(self, student_evaluation_id: int, reference_table_dtos: list[ReferenceTableDTO]
                               ) -> list[ReferenceTableDTO]:
        db_records = [to_reference_orm_foreign_key(student_evaluation_id=student_evaluation_id,
                                                   reference_table_dto=reference_dto)
                      for reference_dto in reference_table_dtos]

        with self._session_factory.begin() as session:
            session.add_all(db_records)
            session.flush()
            return [to_reference_table_dto(db_record) for db_record in db_records]

    def update_reference(self, reference_update_dto: ReferenceUpdateDTO) -> None:
        if reference_update_dto.reference_id:
            with self._session_factory.begin() as session:
                self._reference_CRUD.update_reference(session=session,
                                                      reference_update_dto=reference_update_dto)

    def bulk_update_references(self, reference_update_dtos: list[ReferenceUpdateDTO]) -> None:
        update_data = []

        for dto in reference_update_dtos:
            data = dto.updatable_items_to_dict()
            if data:
                data['id'] = dto.reference_id
                update_data.append(data)

        if not update_data:
            return

        with self._session_factory.begin() as session:
            self._reference_CRUD.bulk_update_references(session=session, bulk_update_data=update_data)

    def delete_references_by_relationship(self, student_evaluation_id: int) -> None:
        with self._session_factory.begin() as session:
            self._reference_CRUD.delete_reference_by_relationship(session=session,
                                                                  student_evaluation_id=student_evaluation_id)

    def get_reference_table_dtos(self, student_evaluation_id: int) -> list[ReferenceTableDTO] | None:
        with self._session_factory.begin() as session:
            references_orm = self._reference_CRUD.get_references_by_relationship(
                session=session, student_evaluation_id=student_evaluation_id)
            if not references_orm:
                return None

            return [to_reference_table_dto(reference_orm) for reference_orm in references_orm]

    def get_reference_table_dto(self, reference_id: int) -> ReferenceTableDTO | None:
        with self._session_factory() as session:
            reference_orm = self._reference_CRUD.get_by_id(session=session, record_id=reference_id)
            return to_reference_table_dto(reference_orm=reference_orm) if reference_orm else None

    @staticmethod
    def export_table_to_excel(reference_table_dtos: list[ReferenceTableDTO],
                              export_path: Path) -> None:
        export_names = [ReferenceTableDTO.Fields.STUDENT_REFERENCE, ReferenceTableDTO.Fields.CROSS_REFERENCE,
                        ReferenceTableDTO.Fields.VERIFICATION_STATUS, ReferenceTableDTO.Fields.RELEVANCE,
                        ReferenceTableDTO.Fields.REFERENCE_TYPE, ReferenceTableDTO.Fields.EVIDENCE_LEVEL,
                        ReferenceTableDTO.Fields.YEAR]

        dict_to_export = [{k: asdict(dto)[k] for k in export_names if k in asdict(dto)}
                          for dto in reference_table_dtos]

        df = pd.DataFrame(dict_to_export)

        with pd.ExcelWriter(export_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Références", index=False)
            worksheet = writer.sheets["Références"]

            for col in worksheet.columns:
                cell_max_len = 0

                col_letter = col[0].column_letter
                for cell in col:
                    if cell.value is not None:
                        cell.alignment = cell.alignment.copy(horizontal="left", vertical="top", wrap_text=True)
                        cell_max_len = max(cell_max_len, len(str(cell.value)))

                worksheet.column_dimensions[col_letter].width = min(cell_max_len + 6, 50)

            for row_idx, row in enumerate(worksheet.iter_rows(min_row=2), start=2):
                max_lines = 1
                for cell in row:
                    if cell.value is not None:
                        col_width = worksheet.column_dimensions[cell.column_letter].width
                        text_length = len(str(cell.value))
                        if col_width > 3:
                            lines = (text_length // int(col_width - 3)) + 1
                            max_lines = max(max_lines, lines)

                worksheet.row_dimensions[row_idx].height = max(max_lines * 12, 20)

    def get_evidence_level_pie_chart_dto(self, reference_table_dtos: list[ReferenceTableDTO]
                                         ) -> EvidenceLevelPieChartDTO:

        df = pd.DataFrame([asdict(reference_table_dto) for reference_table_dto in reference_table_dtos])

        df_filtered = self._filtered_relevant_valid_references(df=df)

        counts = df_filtered[ReferenceTableDTO.Fields.EVIDENCE_LEVEL].value_counts(dropna=False).to_dict()

        return EvidenceLevelPieChartDTO(high_count=counts.get(EvidenceLevelEnum.HIGH, 0),
                                        moderate_count=counts.get(EvidenceLevelEnum.MODERATE, 0),
                                        low_count=counts.get(EvidenceLevelEnum.LOW, 0),
                                        very_low_count=counts.get(EvidenceLevelEnum.VERY_LOW, 0),
                                        no_evidence_count=counts.get(EvidenceLevelEnum.NO_EVIDENCE, 0))

    def get_reference_type_stacked_bar_chart_dto(self, reference_table_dtos: list[ReferenceTableDTO]
                                                 ) -> ReferenceTypeStackedBarChartDTO:
        df = pd.DataFrame([asdict(reference_table_dto) for reference_table_dto in reference_table_dtos])

        year_interval = 14
        # Add 1 year for the publication in the 4th quarter published for the next year
        start_year = (datetime.now().year + 1) - year_interval

        full_year_range = list(range(start_year + 1, (start_year + year_interval + 1)))
        na_label = "N/A"
        x_labels = [na_label, f"{start_year} et -"] + [str(year) for year in full_year_range]
        y_stacked_labels = [ReferenceTypeEnum.SCIENTIFIC_PEER_REVIEW, ReferenceTypeEnum.SCIENTIFIC_NO_REVIEW,
                            ReferenceTypeEnum.GREY]

        df_filtered = self._filtered_relevant_valid_references(df=df)
        df_filtered[ReferenceTableDTO.Fields.YEAR] = pd.to_numeric(df_filtered[ReferenceTableDTO.Fields.YEAR],
                                                                   errors='coerce')

        conditions = [df_filtered[ReferenceTableDTO.Fields.YEAR].isna(),
                      df_filtered[ReferenceTableDTO.Fields.YEAR] < start_year]

        choices = [na_label, f"{start_year} et -"]

        df_filtered['x_labels'] = np.select(
            conditions, choices, default=df_filtered[ReferenceTableDTO.Fields.YEAR].astype("Int64").astype(str))

        df_filtered['x_labels'] = pd.Categorical(df_filtered['x_labels'], categories=x_labels, ordered=True)

        df_matrix = df_filtered.groupby(['x_labels', ReferenceTableDTO.Fields.REFERENCE_TYPE]
                                        ).size().unstack(fill_value=0)

        df_standardized = df_matrix.reindex(index=x_labels,
                                            columns=y_stacked_labels,
                                            fill_value=0)

        return ReferenceTypeStackedBarChartDTO(
            bins=df_standardized.index.to_numpy(),
            scientific_review_counts=df_standardized[ReferenceTypeEnum.SCIENTIFIC_PEER_REVIEW].to_numpy(),
            scientific_no_review_counts=df_standardized[ReferenceTypeEnum.SCIENTIFIC_NO_REVIEW].to_numpy(),
            grey_counts=df_standardized[ReferenceTypeEnum.GREY].to_numpy())

    @staticmethod
    def _filtered_relevant_valid_references(df: pd.DataFrame) -> pd.DataFrame:
        return df[
            (df[ReferenceTableDTO.Fields.VERIFICATION_STATUS] == ReferenceVerificationStatusEnum.VALID) &
            (df[ReferenceTableDTO.Fields.RELEVANCE] == RelevanceLevelEnum.RELEVANT)]