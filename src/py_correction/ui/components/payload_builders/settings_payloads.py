from enum import StrEnum

from src.py_correction.core.domains.shared.shared_dtos import ComboBoxPayload, WidgetItem
from src.py_correction.core.domains.shared.shared_enums import AutofillOptions
from src.py_correction.core.theme_manager import ThemeOptions
from src.py_correction.engine.reference.csl.csl_enum import CitationStyle


class ThemesComboBoxLabels(StrEnum):
    DARK = "Mode sombre"
    LIGHT = "Mode clair"
    SYSTEM = "Paramètre du système"


class EvaluationAutofillOptionsComboBoxLabels(StrEnum):
    NONE = "Aucun remplissage automatique"
    LAST_ENTRY = "Remplir selon la dernière entrée valide"
    MOST_FREQUENT = "Remplir selon l'entrée la plus fréquente"


class CitationStyleComboBoxLabels(StrEnum):
    APA_7TH_EDITION_UDM = "APA 7e édition - UdM"


THEME_OPTIONS_WIDGET_ITEMS = [WidgetItem(label=ThemesComboBoxLabels.DARK, internal_value=ThemeOptions.DARK),
                              WidgetItem(label=ThemesComboBoxLabels.LIGHT, internal_value=ThemeOptions.LIGHT),
                              WidgetItem(label=ThemesComboBoxLabels.SYSTEM, internal_value=ThemeOptions.SYSTEM)]

EVALUATION_AUTOFILL_OPTIONS_WIDGET_ITEMS = [WidgetItem(label=EvaluationAutofillOptionsComboBoxLabels.NONE,
                                                       internal_value=AutofillOptions.NONE),
                                            WidgetItem(label=EvaluationAutofillOptionsComboBoxLabels.LAST_ENTRY,
                                                       internal_value=AutofillOptions.LAST_ENTRY),
                                            WidgetItem(label=EvaluationAutofillOptionsComboBoxLabels.MOST_FREQUENT,
                                                       internal_value=AutofillOptions.MOST_FREQUENT)]

CITATION_STYLE_WIDGET_ITEMS = [WidgetItem(label=CitationStyleComboBoxLabels.APA_7TH_EDITION_UDM,
                                          internal_value=CitationStyle.APA_7th_EDITION_UDM)]


def get_theme_combo_box_payload(current_selection: ThemeOptions) -> ComboBoxPayload[ThemeOptions]:
    return ComboBoxPayload(current_data_selection=current_selection,
                           items=THEME_OPTIONS_WIDGET_ITEMS,
                           is_enabled=True)


def get_evaluation_autofill_combo_box_payload(current_selection: AutofillOptions | None
                                              ) -> ComboBoxPayload[AutofillOptions | None]:
    return ComboBoxPayload(current_data_selection=current_selection,
                           items=EVALUATION_AUTOFILL_OPTIONS_WIDGET_ITEMS,
                           is_enabled=True)


def get_citation_style_combo_box_payload(current_selection: CitationStyle) -> ComboBoxPayload[CitationStyle]:
    # Disable the combo box, because there is only one style available at the moment. To be enabled when more style
    # will be added.
    return ComboBoxPayload(current_data_selection=current_selection,
                           items=CITATION_STYLE_WIDGET_ITEMS,
                           is_enabled=False)


def get_citation_style_label(current_style: CitationStyle) -> CitationStyleComboBoxLabels | str:
    for widget_item in CITATION_STYLE_WIDGET_ITEMS:
        if widget_item.internal_value == current_style:
            return widget_item.label

    return "Aucun style de citation n'a été configuré"
