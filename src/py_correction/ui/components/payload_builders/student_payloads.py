from enum import StrEnum

from src.py_correction.core.domains.shared.shared_dtos import ComboBoxPayload, SelectionWidgetDTO, WidgetItem


class StudentComboBoxLabels(StrEnum):
    NO_STUDENT = "--- Aucun étudiant n'a été importée pour ce cours. ---"


def _get_no_student_payload() -> ComboBoxPayload:
    return ComboBoxPayload(current_data_selection=None,
                           items=[WidgetItem(label=StudentComboBoxLabels.NO_STUDENT,
                                             internal_value=None)],
                           is_enabled=False)


def get_student_id_combo_box_payload(current_data_selection: int | None,
                                     student_selection_dtos: list[SelectionWidgetDTO] | None
                                     ) -> ComboBoxPayload[int | None]:
    if not student_selection_dtos:
        return _get_no_student_payload()

    if isinstance(student_selection_dtos, list):
        combo_box_items = [WidgetItem(label=student_selection_dto.label, internal_value=student_selection_dto.id)
                           for student_selection_dto in student_selection_dtos]
        return ComboBoxPayload(current_data_selection=current_data_selection, items=combo_box_items,
                               is_enabled=True)

    return _get_no_student_payload()
