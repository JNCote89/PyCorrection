from enum import StrEnum
from pathlib import Path

from src.py_correction.core.domains.shared.shared_dtos import ComboBoxPayload, WidgetItem


class TemplateComboBoxLabels(StrEnum):
    EMPTY_DIRECTORY = "--- Aucun gabarit de corrections n'a été importé pour ce cours. ---"
    EMPTY_EVALUATION_LIST = "--- Aucune évaluation n'a été importée pour ce cours. ---"
    NO_CHOICE = "--- Veuillez choisir un gabarit de correction (Recommencer la sélection). ---"
    NO_EXCEL_SHEET = "--- Veuillez choisir une feuille Excel. ---"
    ROW_SELECTION = "--- Veuillez choisir un mot clé pour la rangée. ---"
    NO_ROW_SELECTION = "--- Veuillez choisir un mot clé pour la rangée en premier. ---"
    COLUMN_SELECTION = "--- Veuillez choisir un mot clé pour la colonne. ---"


def _get_empty_directory_payload() -> ComboBoxPayload[None]:
    return ComboBoxPayload(current_data_selection=None,
                           items=[WidgetItem(label=TemplateComboBoxLabels.EMPTY_DIRECTORY, internal_value=None)],
                           is_enabled=False)


def _get_empty_evaluation_list_payload() -> ComboBoxPayload[None]:
    return ComboBoxPayload(current_data_selection=None,
                           items=[WidgetItem(label=TemplateComboBoxLabels.EMPTY_EVALUATION_LIST, internal_value=None)],
                           is_enabled=False)


def _get_no_excel_sheet_payload() -> ComboBoxPayload[None]:
    return ComboBoxPayload(current_data_selection=None,
                           items=[WidgetItem(label=TemplateComboBoxLabels.NO_EXCEL_SHEET, internal_value=None)],
                           is_enabled=False)


def _get_no_row_selection_payload() -> ComboBoxPayload[None]:
    return ComboBoxPayload(current_data_selection=None,
                           items=[WidgetItem(label=TemplateComboBoxLabels.NO_ROW_SELECTION, internal_value=None)],
                           is_enabled=False)


def _add_no_choice_widget_item(widget_items: list[WidgetItem]) -> list[WidgetItem]:
    no_choice_widget_item = WidgetItem(label=TemplateComboBoxLabels.NO_CHOICE, internal_value=None)

    return [no_choice_widget_item] + widget_items


def _add_row_selection_widget_item(widget_items: list[WidgetItem]) -> list[WidgetItem]:
    no_choice_widget_item = WidgetItem(label=TemplateComboBoxLabels.ROW_SELECTION, internal_value=None)

    return [no_choice_widget_item] + widget_items


def _add_column_selection_widget_item(widget_items: list[WidgetItem]) -> list[WidgetItem]:
    no_choice_widget_item = WidgetItem(label=TemplateComboBoxLabels.COLUMN_SELECTION, internal_value=None)

    return [no_choice_widget_item] + widget_items


def get_template_combo_box_payload(current_data_selection: Path | None,
                                   items: list[Path] | None, has_evaluation: bool = True
                                   ) -> ComboBoxPayload[Path | None]:
    if not has_evaluation:
        return _get_empty_evaluation_list_payload()
    if not items:
        return _get_empty_directory_payload()

    database_widget_items = [WidgetItem(label=path.name, internal_value=path)
                             for path in items] # type: ignore[arg-type]
    combo_box_items = _add_no_choice_widget_item(widget_items=database_widget_items)

    return ComboBoxPayload(current_data_selection=current_data_selection, items=combo_box_items,
                           is_enabled=True)


def get_sheet_combo_box_payload(current_data_selection: str | None, items: list[str] | None
                                ) -> ComboBoxPayload[str | None]:
    if not items:
        return _get_no_excel_sheet_payload()

    database_widget_items = [WidgetItem(label=sheet_name, internal_value=sheet_name)
                             for sheet_name in items] # type: ignore[arg-type]

    return ComboBoxPayload(current_data_selection=current_data_selection, items=database_widget_items,
                           is_enabled=True)


def get_row_keyword_combo_box_payload(current_data_selection: str | None, items: list[str] | None
                                      ) -> ComboBoxPayload[str | None]:
    if not items:
        return _get_no_excel_sheet_payload()

    database_widget_items = [WidgetItem(label=row_keyword, internal_value=row_keyword)
                             for row_keyword in items] # type: ignore[arg-type]
    combo_box_items = _add_row_selection_widget_item(widget_items=database_widget_items)

    return ComboBoxPayload(current_data_selection=current_data_selection, items=combo_box_items, is_enabled=True)


def get_column_keyword_combo_box_payload(current_data_selection: str | None, items: list[str] | None,
                                         no_row_is_selected: bool) -> ComboBoxPayload[str | None]:
    if no_row_is_selected:
        return _get_no_row_selection_payload()
    if not items:
        return _get_no_excel_sheet_payload()

    database_widget_items = [WidgetItem(label=column_keyword, internal_value=column_keyword)
                             for column_keyword in items] # type: ignore[arg-type]
    combo_box_items = _add_column_selection_widget_item(widget_items=database_widget_items)

    return ComboBoxPayload(current_data_selection=current_data_selection, items=combo_box_items, is_enabled=True)
