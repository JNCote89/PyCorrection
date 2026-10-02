from pathlib import Path
from typing import override

from PySide6.QtCore import QRegularExpression, QSignalBlocker, Qt, Signal, Slot
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import QLineEdit, QListWidgetItem, QPushButton, QVBoxLayout, QWidget

from src.py_correction.core.domains.evaluation.evaluation_dtos import EvaluationCreateDTO
from src.py_correction.core.domains.shared.shared_dtos import ComboBoxPayload, SelectionWidgetDTO
from src.py_correction.core.domains.shared.shared_enums import ImportTypeEnum
from src.py_correction.engine.helpers import decimal_helpers
from src.py_correction.ui.components.base_components.widget_lifecycle_mixin import WidgetLifecycleMixin
from src.py_correction.ui.components.default_widgets.labels import DefaultLabel
from src.py_correction.ui.components.layouts import DefaultFormLayout
from src.py_correction.ui.components.partial_widgets.combo_boxes import PartialComboBox
from src.py_correction.ui.components.partial_widgets.import_widgets import PartialDragAndDropWidget
from src.py_correction.ui.components.partial_widgets.list_widgets import PartialPlaceholderListWidget


class EvaluationImportFormWidget(QWidget, WidgetLifecycleMixin):
    _is_final_component = True

    evaluationFormSubmitted = Signal(EvaluationCreateDTO)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self.setMinimumHeight(200)

        self._evaluation_title_input = QLineEdit()
        self._evaluation_title_input.setPlaceholderText("e.g., Plan de travail")
        self._evaluation_title_input.setMaxLength(256)
        self._evaluation_title_input_label = DefaultLabel(text="Titre de l'évaluation",
                                                          subtext="Maximum de 256 caractères")

        self._maximum_grade_input = QLineEdit()
        self._maximum_grade_input.setPlaceholderText("e.g., 100,00")
        self._maximum_grade_input_label = DefaultLabel(text="Note maximale",
                                                       subtext="Maximum de 3 chiffres et 2 décimales")

        self._submit_button = QPushButton("Soumettre")
        self._submit_button.setEnabled(False)

    @override
    def _assemble_layout(self) -> None:
        main_layout = QVBoxLayout(self)

        form_layout = DefaultFormLayout()
        form_layout.addRow(self._evaluation_title_input_label, self._evaluation_title_input)
        form_layout.addRow(self._maximum_grade_input_label, self._maximum_grade_input)

        main_layout.addLayout(form_layout)
        main_layout.addWidget(self._submit_button, alignment=Qt.AlignmentFlag.AlignHCenter)  # type: ignore
        main_layout.addStretch()

    @override
    def _connect_internal_signals(self) -> None:
        self._setup_validators()

        self._evaluation_title_input.textChanged.connect(self._validate_form)
        self._maximum_grade_input.textChanged.connect(self._validate_form)
        self._submit_button.clicked.connect(self._on_submit)

    def _setup_validators(self):
        evaluation_title_regex = QRegularExpression(r"^.{1,256}$")
        self._evaluation_title_input.setValidator(QRegularExpressionValidator(evaluation_title_regex, self))

        maximum_grade_regex = QRegularExpression(r"^\d{1,3}([\.,]\d{1,2})?$")
        self._maximum_grade_input.setValidator(QRegularExpressionValidator(maximum_grade_regex, self))

    @Slot()
    def _validate_form(self) -> None:
        evaluation_title_valid = self._evaluation_title_input.hasAcceptableInput()

        maximum_grade_valid = self._maximum_grade_input.hasAcceptableInput()

        form_is_valid = evaluation_title_valid and maximum_grade_valid

        self._submit_button.setEnabled(form_is_valid)

    @Slot()
    def _on_submit(self) -> None:
        evaluation_title = self._evaluation_title_input.text().strip()
        maximum_grade = self._maximum_grade_input.text().strip()

        safe_maximum_grade = decimal_helpers.safe_decimal(maximum_grade)

        evaluation = EvaluationCreateDTO(title=evaluation_title,
                                         maximum_grade=safe_maximum_grade,
                                         import_type=ImportTypeEnum.MANUAL)

        self.evaluationFormSubmitted.emit(evaluation)

        self._evaluation_title_input.clear()
        self._maximum_grade_input.clear()


class EvaluationTemplateFileImportWidget(PartialDragAndDropWidget):
    _is_final_component = True

    evaluationTemplateFileSubmitted = Signal(Path)

    _LABEL = "ou glisser les fichiers Excel des gabarits de correction à importer pour le cours"
    _EXTENSIONS = (".xlsx", ".xls")
    _FILE_DIALOG_WINDOW_TITLE = "Sélectionner les gabarits de correction Excel à importer pour le cours"

    def __init__(self, parent: QWidget | None = None):
        super().__init__(label=self._LABEL, extensions=self._EXTENSIONS,
                         file_dialog_window_title=self._FILE_DIALOG_WINDOW_TITLE, allow_multiple=True,
                         parent=parent)
        self._init_ui()

    @override
    def _process_import_file(self, file_path: Path) -> None:
        self.evaluationTemplateFileSubmitted.emit(file_path)


class EvaluationsListWidget(PartialPlaceholderListWidget):
    _is_final_component = True

    evaluationIDChanged = Signal(object)
    emptyListStatusChanged = Signal(bool)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._init_ui()

        self.set_placeholder_text("Aucune évaluation disponible pour ce cours. Veuillez en ajouter via "
                                  "l'importation manuelle ou recommencer l'imporation avec un fichier GeNote "
                                  "contenant l'ensemble des évaluations. Il sera par la suite possible d'associer "
                                  "un gabarit de correction avec l'évaluation créée.")

    @override
    def _connect_internal_signals(self) -> None:
        self.currentRowChanged.connect(self._on_row_changed)

    @Slot(int)
    def _on_row_changed(self, row: int) -> None:
        if row < 0:
            self.evaluationIDChanged.emit(None)

        item = self.item(row)
        evaluation_id = item.data(Qt.ItemDataRole.UserRole)
        self.evaluationIDChanged.emit(evaluation_id)

    def _set_row(self) -> None:
        if self.currentRow() < 0:
            self.setCurrentRow(0)

    def _check_empty_state(self) -> None:
        if self.count() == 0:
            self.emptyListStatusChanged.emit(True)

    @Slot(SelectionWidgetDTO)
    def update_list(self, evaluations: list[SelectionWidgetDTO] | None) -> None:
        with QSignalBlocker(self):
            self.clear()
            if isinstance(evaluations, list):
                for evaluation in evaluations:
                    item = QListWidgetItem(evaluation.label)
                    item.setData(Qt.ItemDataRole.UserRole, evaluation.id)
                    self.addItem(item)

        self._check_empty_state()
        self._set_row()


class TemplateFileComboBox(PartialComboBox):
    _is_final_component = True

    templateFileSelectionChanged = Signal(Path)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._init_ui()

    @override
    def _connect_downstream_signals(self) -> None:
        self.currentIndexChanged.connect(self._on_index_changed)

    @Slot(ComboBoxPayload)
    @override
    def populate_combo_box(self, payload: ComboBoxPayload[Path | None]) -> None:
        # Must override the parent class, because the index matching with the user data does not work with the Path
        # object, must check against the string label that return the name of the file instead of the Path
        with QSignalBlocker(self):
            self.clear()
            for item in payload.items:
                self.addItem(item.label, item.internal_value)

        self._match_current_data_selection_index(current_data_selection=payload.current_data_selection)
        self.setEnabled(payload.is_enabled)

    @Slot(int)
    @override
    def _on_index_changed(self, _index: int) -> None:
        template_selected = self.currentData()
        self.templateFileSelectionChanged.emit(template_selected)

    @override
    def _match_current_data_selection_index(self, current_data_selection: Path | None) -> None:
        # Must override the method to handle the path object
        current_data_selection = current_data_selection.name if current_data_selection else ""
        matching_index = self.findText(current_data_selection)
        if matching_index != -1:
            self.setCurrentIndex(matching_index)
        else:
            if self.currentIndex() == 0:
                self._on_index_changed(0)
            else:
                self.setCurrentIndex(0)


class SheetNameComboBox(PartialComboBox):
    _is_final_component = True

    sheetNameSelectionChanged = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._init_ui()

    @override
    def _connect_downstream_signals(self) -> None:
        self.currentIndexChanged.connect(self._on_index_changed)

    @Slot(int)
    @override
    def _on_index_changed(self, _index: int) -> None:
        selected_sheet = self.currentData()
        self.sheetNameSelectionChanged.emit(selected_sheet)


class RowKeywordComboBox(PartialComboBox):
    _is_final_component = True

    rowKeywordSelectionChanged = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._init_ui()

    @override
    def _connect_downstream_signals(self) -> None:
        self.currentIndexChanged.connect(self._on_index_changed)

    @Slot(int)
    @override
    def _on_index_changed(self, _index: int) -> None:
        selected_keyword = self.currentData()
        self.rowKeywordSelectionChanged.emit(selected_keyword)


class ColumnKeywordComboBox(PartialComboBox):
    _is_final_component = True

    columnKeywordSelectionChanged = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._init_ui()

    @override
    def _connect_downstream_signals(self) -> None:
        self.currentIndexChanged.connect(self._on_index_changed)

    @Slot(int)
    @override
    def _on_index_changed(self, _index: int) -> None:
        selected_keyword = self.currentData()
        self.columnKeywordSelectionChanged.emit(selected_keyword)
