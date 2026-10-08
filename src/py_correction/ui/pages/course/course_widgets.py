from pathlib import Path
import re
from typing import Any, override

from PySide6.QtCore import (QAbstractTableModel, QModelIndex, QObject, QPersistentModelIndex, QRegularExpression, Qt,
                            Signal, Slot)
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import QLineEdit, QPushButton, QVBoxLayout, QWidget

from src.py_correction.core import nuitka_helpers
from src.py_correction.core.domains.course.course_dtos import CourseCreateDTO, CourseTableDTO
from src.py_correction.core.domains.shared.shared_enums import ImportTypeEnum
from src.py_correction.ui.components.base_components.widget_lifecycle_mixin import WidgetLifecycleMixin
from src.py_correction.ui.components.default_widgets.labels import DefaultLabel
from src.py_correction.ui.components.layouts import DefaultFormLayout
from src.py_correction.ui.components.partial_widgets.import_widgets import PartialDragAndDropWidget
from src.py_correction.ui.components.partial_widgets.table_views import PartialReactiveTableView
from src.py_correction.utils import date_format


class GeNoteImportWidget(PartialDragAndDropWidget):
    _is_final_component = True

    geNoteGradeFilePathSubmitted = Signal(Path)
    geNoteImportFailed = Signal(str)

    LABEL = "ou glisser le fichier Excel GeNote avec le format notes-SIGXXXGrYY-S20XX.xlsx"
    EXTENSIONS = (".xlsx", ".xls")
    FILE_DIALOG_WINDOW_TITLE = "Sélectionner le fichier Excel GeNote avec le format notes-SIGXXXGrYY-S20XX"

    def __init__(self, parent: QWidget | None = None):
        super().__init__(label=self.LABEL, extensions=self.EXTENSIONS,
                         file_dialog_window_title=self.FILE_DIALOG_WINDOW_TITLE, allow_multiple=True,
                         parent=parent)
        self._init_ui()

    @override
    def _process_import_file(self, file_path: Path) -> None:
        genote_file_regex_pattern = r"^notes-[A-Z]{3}\d{3}Gr\d+-[A-Z]\d{4}(\.xlsx)?$"
        file_path = Path(file_path)
        if re.match(genote_file_regex_pattern, file_path.name):
            self.geNoteGradeFilePathSubmitted.emit(file_path)
        else:
            self.geNoteImportFailed.emit(file_path.name)


class CourseImportFormWidget(QWidget, WidgetLifecycleMixin):
    _is_final_component = True

    courseFormSubmitted = Signal(CourseCreateDTO)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self.setMinimumHeight(400)

        self._semester_input = QLineEdit()
        self._semester_input.setPlaceholderText("e.g., A2026")
        self._semester_input_label = DefaultLabel(text="Semestre",
                                                  subtext="Indiquer le semestre (A, H ou E) suivi de l'année à 4 "
                                                          "chiffres")

        self._course_code_input = QLineEdit()
        self._course_code_input.setPlaceholderText("e.g., ENV847")
        self._course_code_input_label = DefaultLabel(text="Sigle pour le cours",
                                                     subtext="Selon le format 3 lettres et 3 chiffres sans espace")

        self._course_name_input = QLineEdit()
        self._course_name_input.setPlaceholderText("e.g., Adaptation aux changements climatiques")
        self._course_name_input.setMaxLength(256)
        self._course_name_input_label = DefaultLabel(text="Nom du cours",
                                                     subtext="Maximum de 256 caractères")

        self._group_input = QLineEdit()
        self._group_input.setPlaceholderText("e.g., 99")
        self._group_input_label = DefaultLabel(text="Groupe",
                                               subtext="Indiquer le groupe à 2 chiffres")

        self._submit_button = QPushButton("Soumettre")
        self._submit_button.setEnabled(False)

    @override
    def _assemble_layout(self) -> None:
        main_layout = QVBoxLayout(self)

        form_layout = DefaultFormLayout()
        form_layout.addRow(self._semester_input_label, self._semester_input)
        form_layout.addRow(self._course_code_input_label, self._course_code_input)
        form_layout.addRow(self._course_name_input_label, self._course_name_input)
        form_layout.addRow(self._group_input_label, self._group_input)

        main_layout.addLayout(form_layout)
        main_layout.addWidget(self._submit_button, alignment=Qt.AlignmentFlag.AlignHCenter)  # type: ignore
        main_layout.addStretch()

    @override
    def _connect_internal_signals(self) -> None:
        self._setup_validators()

        nuitka_helpers.safe_connect(signal=self._course_name_input.textChanged, slot=lambda _: self._validate_form())
        nuitka_helpers.safe_connect(signal=self._semester_input.textChanged, slot=lambda _: self._validate_form())
        nuitka_helpers.safe_connect(signal=self._course_code_input.textChanged, slot=lambda _: self._validate_form())
        nuitka_helpers.safe_connect(signal=self._group_input.textChanged, slot=lambda _: self._validate_form())
        nuitka_helpers.safe_connect(signal=self._submit_button.clicked, slot=self._on_submit)

    def _setup_validators(self) -> None:
        semester_regex = QRegularExpression(r"^[AHEahe]{1}\d{4}$")
        self._semester_input.setValidator(QRegularExpressionValidator(semester_regex, self))

        course_id_regex = QRegularExpression(r"^[A-Za-z]{3}\d{3}$")
        self._course_code_input.setValidator(QRegularExpressionValidator(course_id_regex, self))

        course_name_regex = QRegularExpression(r"^[\p{L}\s\-\']{1,256}$",
                                               QRegularExpression.PatternOption.UseUnicodePropertiesOption)  # type: ignore[arg-type]
        self._course_name_input.setValidator(QRegularExpressionValidator(course_name_regex, self))

        group_regex = QRegularExpression(r"^\d{2}$")
        self._group_input.setValidator(QRegularExpressionValidator(group_regex, self))

    @Slot()
    def _validate_form(self) -> None:
        semester_is_valid = self._semester_input.hasAcceptableInput()
        course_id_is_valid = self._course_code_input.hasAcceptableInput()
        course_name_is_valid = self._course_name_input.hasAcceptableInput()
        group_is_valid = self._group_input.hasAcceptableInput()

        form_is_valid = semester_is_valid and course_id_is_valid and course_name_is_valid and group_is_valid
        self._submit_button.setEnabled(form_is_valid)

    @Slot()
    def _on_submit(self):
        course_dto = CourseCreateDTO(semester=self._semester_input.text().upper().strip(),
                                     code=self._course_code_input.text().upper().strip(),
                                     name=self._course_name_input.text().strip(),
                                     group=self._group_input.text().strip(),
                                     creation_date=date_format.get_utc_now(),
                                     import_type=ImportTypeEnum.MANUAL,
                                     genote_filename=None)

        self.courseFormSubmitted.emit(course_dto)

        self._semester_input.clear()
        self._course_code_input.clear()
        self._course_name_input.clear()
        self._group_input.clear()


class CourseTableModel(QAbstractTableModel):
    def __init__(self, parent: QObject | None = None):
        super().__init__(parent=parent)
        self._course_table_dtos: list[CourseTableDTO] = []

        self._headers = CourseTableDTO.get_headers()
        self._field_names = CourseTableDTO.get_field_names()

    def set_courses(self, course_table_dtos: list[CourseTableDTO]) -> None:
        self.beginResetModel()
        self._course_table_dtos = course_table_dtos
        self.endResetModel()

    def get_column_index(self, field_name: str) -> int:
        try:
            return self._field_names.index(field_name)
        except ValueError:
            return -1

    @override
    def rowCount(self, parent: QPersistentModelIndex | QModelIndex = QModelIndex()) -> int:
        return len(self._course_table_dtos)

    @override
    def columnCount(self, parent: QPersistentModelIndex | QModelIndex = QModelIndex()) -> int:
        return len(self._headers)

    @override
    def data(self, index: QPersistentModelIndex | QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any | None:
        if not index.isValid():
            return None

        course = self._course_table_dtos[index.row()]
        col = index.column()
        field_name = self._field_names[col]

        if 0 <= col < len(self._field_names):
            if field_name == CourseTableDTO.Fields.CREATION_DATE:
                creation_date = getattr(course, field_name)

                if role == Qt.ItemDataRole.DisplayRole:
                    return date_format.return_user_date_str(creation_date)
                if role == Qt.ItemDataRole.EditRole:
                    return creation_date

            if role == Qt.ItemDataRole.DisplayRole:
                return getattr(course, field_name)

        return None

    @override
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole
                   ) -> str | None:
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self._headers[section]
        return None


class CourseTableView(PartialReactiveTableView):
    _is_final_component = True

    def __init__(self, table_model: QAbstractTableModel, parent: QWidget | None = None):
        self._sorting_column = CourseTableDTO.Fields.CREATION_DATE

        super().__init__(column_index_stretch=2, table_model=table_model, parent=parent)
        self._init_ui()

    @override
    def _configure_table_sorting(self) -> None:
        creation_date_index = self.table_model.get_column_index(self._sorting_column) # type: ignore[arg-type]
        self.sortByColumn(creation_date_index, Qt.SortOrder.DescendingOrder) # type: ignore[arg-type]
