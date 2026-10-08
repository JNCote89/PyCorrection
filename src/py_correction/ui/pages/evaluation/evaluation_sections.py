from pathlib import Path
from typing import override

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QVBoxLayout, QWidget

from src.py_correction.core import nuitka_helpers
from src.py_correction.core.domains.evaluation.evaluation_dtos import EvaluationCreateDTO
from src.py_correction.core.domains.shared.shared_dtos import ComboBoxPayload, SelectionWidgetDTO
from src.py_correction.core.domains.shared.shared_enums import AutofillOptions
from src.py_correction.engine.excel.excel_operations import MAX_KEYWORD_COUNT
from src.py_correction.ui.components.base_components.widget_lifecycle_mixin import WidgetLifecycleMixin
from src.py_correction.ui.components.default_widgets.collapsible_sections import DefaultCollapsibleSection
from src.py_correction.ui.components.default_widgets.labels import DefaultLabel
from src.py_correction.ui.components.layouts import DefaultGridLayout
from src.py_correction.ui.pages.evaluation.evaluation_widgets import (ColumnKeywordComboBox, EvaluationImportFormWidget,
                                                                      EvaluationTemplateFileImportWidget,
                                                                      EvaluationsListWidget, RowKeywordComboBox,
                                                                      SheetNameComboBox, TemplateFileComboBox)


class EvaluationFormImportCollapsibleSection(QWidget, WidgetLifecycleMixin):
    _is_final_component = True

    evaluationFormSubmitted = Signal(EvaluationCreateDTO)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self.collapsible_section = DefaultCollapsibleSection(title="Création manuelle d'une évaluation",
                                                             subtitle="Seulement pour les évaluations non associées à "
                                                                      "une feuille GeNote")
        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self._evaluation_import_form_widget = EvaluationImportFormWidget()

    @override
    def _assemble_layout(self) -> None:
        self.collapsible_section.add_widget(self._evaluation_import_form_widget)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.collapsible_section)

    @override
    def _connect_downstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._evaluation_import_form_widget.evaluationFormSubmitted,
                                    slot=self.evaluationFormSubmitted)

    def set_collapsible_section_state(self, expanded: bool) -> None:
        self.collapsible_section.set_expand_state(expanded=expanded)


class EvaluationTemplateImportGroupBox(QGroupBox, WidgetLifecycleMixin):
    _is_final_component = True

    evaluationTemplateFileSubmitted = Signal(Path)

    def __init__(self, parent: QWidget | None = None):
        super().__init__("Importation des gabarits de correction Excel", parent)
        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self._evaluation_template_import_widget = EvaluationTemplateFileImportWidget()

    @override
    def _assemble_layout(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self._evaluation_template_import_widget)

    @override
    def _connect_downstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._evaluation_template_import_widget.evaluationTemplateFileSubmitted,
                                    slot=self.evaluationTemplateFileSubmitted)

    @Slot(Path)
    def update_template_import_starting_directory(self, starting_directory: Path) -> None:
        self._evaluation_template_import_widget.update_starting_path_directory(path_directory=starting_directory)


class EvaluationManagementGroupBox(QGroupBox, WidgetLifecycleMixin):
    _is_final_component = True

    evaluationIDChanged = Signal(object)
    emptyListStatusChanged = Signal(bool)

    templateFileSelectionChanged = Signal(Path)
    sheetNameSelectionChanged = Signal(str)
    rowKeywordSelectionChanged = Signal(str)
    columnKeywordSelectionChanged = Signal(str)

    def __init__(self, parent: QWidget | None  = None):
        super().__init__("Gestion des évaluations", parent=parent)
        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self.setMinimumHeight(400)

        self._evaluation_list_widget = EvaluationsListWidget()

        self._template_label = DefaultLabel(text="Gabarit de correction à associer avec "
                                                 "l'évaluation",
                                            alignment_h_flag=Qt.AlignmentFlag.AlignHCenter) # type: ignore[arg-type]
        self._template_file_combo_box = TemplateFileComboBox()

        self._sheet_label = DefaultLabel(text="Feuille où extraire la note finale vers GeNote",
                                         alignment_h_flag=Qt.AlignmentFlag.AlignHCenter) # type: ignore[arg-type]
        self._sheet_name_combo_box = SheetNameComboBox()

        self._keyword_label = DefaultLabel(text="Mots clés pour identifier les coordonnées contenant la note finale à "
                                                "extraire vers GeNote",
                                           subtext=f"Maximum {MAX_KEYWORD_COUNT} mots par cellule et "
                                                   f"doit être unique dans la feuille",
                                           alignment_h_flag=Qt.AlignmentFlag.AlignHCenter) # type: ignore[arg-type]

        self._row_label = DefaultLabel(text="Mot clé pour identifier la rangée")
        self._row_keyword_combo_box = RowKeywordComboBox()

        self._column_label = DefaultLabel(text="Mot clé pour identifier la colonne")
        self._column_keyword_combo_box = ColumnKeywordComboBox()

    @override
    def _assemble_layout(self) -> None:
        main_layout = QHBoxLayout(self)

        left_layout = QVBoxLayout()
        left_layout.addWidget(self._evaluation_list_widget)

        right_layout_grid = DefaultGridLayout()

        right_layout_grid.addWidget(self._template_label, 0, 0, 1, 2)

        right_layout_grid.addWidget(self._template_file_combo_box, 1, 0, 1, 2)

        right_layout_grid.addWidget(self._sheet_label, 2, 0, 1, 2)

        right_layout_grid.addWidget(self._sheet_name_combo_box, 3, 0, 1, 2)

        right_layout_grid.addWidget(self._keyword_label, 4, 0, 1, 2)

        right_layout_grid.addWidget(self._row_label, 5, 0, 1, 1)
        right_layout_grid.addWidget(self._row_keyword_combo_box, 5, 1, 1, 1)

        right_layout_grid.addWidget(self._column_label, 6, 0, 1, 1)
        right_layout_grid.addWidget(self._column_keyword_combo_box, 6, 1, 1, 1)

        self._evaluation_settings_group_box = QGroupBox()
        self._evaluation_settings_group_box.setLayout(right_layout_grid)
        self._evaluation_settings_group_box.setProperty("class", "inner_groupbox")

        main_layout.addWidget(self._evaluation_list_widget, 1)
        main_layout.addWidget(self._evaluation_settings_group_box, 3)

    @override
    def _connect_downstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._evaluation_list_widget.evaluationIDChanged,
                                    slot=self.evaluationIDChanged)
        nuitka_helpers.safe_connect(signal=self._evaluation_list_widget.emptyListStatusChanged,
                                    slot=self.emptyListStatusChanged)

        nuitka_helpers.safe_connect(signal=self._template_file_combo_box.templateFileSelectionChanged,
                                    slot=self.templateFileSelectionChanged)
        nuitka_helpers.safe_connect(signal=self._sheet_name_combo_box.sheetNameSelectionChanged,
                                    slot=self.sheetNameSelectionChanged)
        nuitka_helpers.safe_connect(signal=self._row_keyword_combo_box.rowKeywordSelectionChanged,
                                    slot=self.rowKeywordSelectionChanged)
        nuitka_helpers.safe_connect(signal=self._column_keyword_combo_box.columnKeywordSelectionChanged,
                                    slot=self.columnKeywordSelectionChanged)

    @Slot(SelectionWidgetDTO)
    def update_evaluation_list(self, evaluations: list[SelectionWidgetDTO] | None) -> None:
        self._evaluation_list_widget.update_list(evaluations=evaluations)

    @Slot(ComboBoxPayload)
    def populate_template_file_combo_box(self, payload: ComboBoxPayload[Path | None]) -> None:
        self._template_file_combo_box.populate_combo_box(payload=payload)

    @Slot(ComboBoxPayload)
    def populate_sheet_name_combo_box(self, payload: ComboBoxPayload[str | None]) -> None:
        self._sheet_name_combo_box.populate_combo_box(payload=payload)

    @Slot(ComboBoxPayload)
    def populate_row_keyword_combo_box(self, payload: ComboBoxPayload[str | None]) -> None:
        self._row_keyword_combo_box.populate_combo_box(payload=payload)

    @Slot(ComboBoxPayload)
    def populate_column_keyword_combo_box(self, payload: ComboBoxPayload[str | None]) -> None:
        self._column_keyword_combo_box.populate_combo_box(payload=payload)

    @Slot(AutofillOptions)
    def set_evaluation_settings_group_box_title(self, autofill_option: AutofillOptions) -> None:
        default_label = "Configuration du gabarit de correction associé à l'évaluation"

        if autofill_option != AutofillOptions.NONE:
            self._evaluation_settings_group_box.setTitle(f"{default_label} (remplissage automatique activé)")
        else:
            self._evaluation_settings_group_box.setTitle(default_label)
