from enum import StrEnum

from src.py_correction.core.domains.shared.shared_dtos import ComboBoxPayload, SelectionWidgetDTO, WidgetItem


class EvaluationComboBoxLabels(StrEnum):
    NO_EVALUATION = "--- Aucune évaluation n'a été importée pour ce cours. ---"


def _get_no_evaluation_payload() -> ComboBoxPayload:
    return ComboBoxPayload(current_data_selection=None,
                           items=[WidgetItem(label=EvaluationComboBoxLabels.NO_EVALUATION,
                                             internal_value=None)],
                           is_enabled=False)


def get_evaluation_id_combo_box_payload(current_data_selection: int | None,
                                        evaluation_selection_dtos: list[SelectionWidgetDTO] | None
                                        ) -> ComboBoxPayload[int | None]:
    if not evaluation_selection_dtos:
        return _get_no_evaluation_payload()

    if isinstance(evaluation_selection_dtos, list):
        combo_box_items = [WidgetItem(label=evaluation_selection.label, internal_value=evaluation_selection.id)
                           for evaluation_selection in evaluation_selection_dtos]
        return ComboBoxPayload(current_data_selection=current_data_selection, items=combo_box_items,
                               is_enabled=True)

    return _get_no_evaluation_payload()
