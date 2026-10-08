from typing import Any, override

from PySide6.QtCore import (QAbstractTableModel, QModelIndex, QObject, QPersistentModelIndex, QRegularExpression, Qt,
                            Signal, Slot)
from PySide6.QtGui import QColor, QRegularExpressionValidator
from PySide6.QtWidgets import QLineEdit, QPushButton, QVBoxLayout, QWidget

from src.py_correction.core import nuitka_helpers
from src.py_correction.core.domains.course.course_student_dtos import CourseStudentTableDTO, CourseStudentUpdateDTO
from src.py_correction.core.domains.shared.shared_enums import ImportTypeEnum
from src.py_correction.core.domains.student.student_dtos import StudentCreateDTO
from src.py_correction.ui.components.base_components.widget_lifecycle_mixin import WidgetLifecycleMixin
from src.py_correction.ui.components.default_widgets.labels import DefaultLabel
from src.py_correction.ui.components.layouts import DefaultFormLayout
from src.py_correction.ui.components.partial_widgets.table_views import PartialReactiveTableView


class StudentImportFormWidget(QWidget, WidgetLifecycleMixin):
    _is_final_component = True

    studentFormSubmitted = Signal(StudentCreateDTO)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)

        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self.setMinimumHeight(350)
        self._cip_input = QLineEdit()
        self._cip_input.setPlaceholderText("e.g., cbad1234")
        self._cip_input_label = DefaultLabel(text="CIP",
                                             subtext="Indiquer le CIP unique de l'étudiant à 4 lettres et 4 chiffres "
                                                     "sans espace")

        self._first_name_input = QLineEdit()
        self._first_name_input.setPlaceholderText("e.g., Prénom")
        self._first_name_input_label = DefaultLabel(text="Prénom")

        self._last_name_input = QLineEdit()
        self._last_name_input.setPlaceholderText("e.g., Nom de famille")
        self._last_name_input_label = DefaultLabel(text="Nom de famille")

        self._submit_button = QPushButton("Soumettre")
        self._submit_button.setEnabled(False)

    @override
    def _assemble_layout(self) -> None:
        main_layout = QVBoxLayout(self)

        form_layout = DefaultFormLayout()
        form_layout.addRow(self._cip_input_label, self._cip_input)
        form_layout.addRow(self._first_name_input_label, self._first_name_input)
        form_layout.addRow(self._last_name_input_label, self._last_name_input)

        main_layout.addLayout(form_layout)
        main_layout.addWidget(self._submit_button, alignment=Qt.AlignmentFlag.AlignHCenter) # type: ignore[arg-type]
        main_layout.addStretch()

    @override
    def _connect_internal_signals(self) -> None:
        self._setup_validators()

        nuitka_helpers.safe_connect(signal=self._cip_input.textChanged, slot=lambda _: self._validate_form())
        nuitka_helpers.safe_connect(signal=self._first_name_input.textChanged, slot=lambda _: self._validate_form())
        nuitka_helpers.safe_connect(signal=self._last_name_input.textChanged, slot=lambda _: self._validate_form())

        nuitka_helpers.safe_connect(signal=self._submit_button.clicked, slot=self._on_submit)

    def _setup_validators(self) -> None:
        cip_regex = QRegularExpression(r"^[a-z]{4}\d{4}$")
        self._cip_input.setValidator(QRegularExpressionValidator(cip_regex, self))

        name_regex = QRegularExpression(r"^[\p{L}\s\-\']{1,256}$",
                                        QRegularExpression.PatternOption.UseUnicodePropertiesOption)  # type: ignore[arg-type]

        self._first_name_input.setValidator(QRegularExpressionValidator(name_regex, self))
        self._last_name_input.setValidator(QRegularExpressionValidator(name_regex, self))

    @Slot()
    def _validate_form(self) -> None:
        cip_is_valid = self._cip_input.hasAcceptableInput()
        first_name_is_valid = self._first_name_input.hasAcceptableInput()
        last_name_is_valid = self._last_name_input.hasAcceptableInput()

        form_is_valid = cip_is_valid and first_name_is_valid and last_name_is_valid

        self._submit_button.setEnabled(form_is_valid)

    @Slot()
    def _on_submit(self) -> None:
        course = StudentCreateDTO(cip=self._cip_input.text().lower().strip(),
                                  first_name=self._first_name_input.text().strip(),
                                  last_name=self._last_name_input.text().strip(),
                                  import_type=ImportTypeEnum.MANUAL)

        self.studentFormSubmitted.emit(course)

        self._cip_input.clear()
        self._first_name_input.clear()
        self._last_name_input.clear()


class StudentTableModel(QAbstractTableModel):
    studentStatusChanged = Signal(CourseStudentUpdateDTO)

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent=parent)
        self._course_student_dtos: list[CourseStudentTableDTO] = []

        self._headers = CourseStudentTableDTO.get_headers()
        self._field_names = CourseStudentTableDTO.get_field_names()

    def set_students(self, course_student_table_dtos: list[CourseStudentTableDTO]) -> None:
        self.beginResetModel()
        self._course_student_dtos = course_student_table_dtos
        self.endResetModel()

    def get_column_index(self, field_name: str) -> int:
        try:
            return self._field_names.index(field_name)
        except ValueError:
            return -1

    @override
    def rowCount(self, parent: QPersistentModelIndex | QModelIndex = QModelIndex()) -> int:
        return len(self._course_student_dtos)

    @override
    def columnCount(self, parent: QPersistentModelIndex | QModelIndex = QModelIndex()) -> int:
        return len(self._headers)

    @override
    def flags(self, index: QPersistentModelIndex | QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags  # type: ignore[arg-type]

        base_flags = super().flags(index)
        field_name = self._field_names[index.column()]

        if field_name == CourseStudentTableDTO.Fields.IS_ACTIVE:
            return base_flags | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled

        return base_flags

    @override
    def data(self, index: QPersistentModelIndex | QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any | None:
        if not index.isValid():
            return None

        course_student = self._course_student_dtos[index.row()]
        col = index.column()
        field_name = self._field_names[col]

        is_active = getattr(course_student, CourseStudentTableDTO.Fields.IS_ACTIVE, True)

        if 0 <= col < len(self._field_names):
            if role == Qt.ItemDataRole.DisplayRole:
                if field_name == CourseStudentTableDTO.Fields.IS_ACTIVE:
                    return "Active" if is_active else "Inactive"
                return getattr(course_student, field_name)

            elif role == Qt.ItemDataRole.CheckStateRole and field_name == CourseStudentTableDTO.Fields.IS_ACTIVE:
                return Qt.CheckState.Checked if is_active else Qt.CheckState.Unchecked

            elif role == Qt.ItemDataRole.ForegroundRole:
                if not is_active:
                    return QColor(Qt.GlobalColor.gray)

        return None

    @override
    def setData(self, index: QPersistentModelIndex | QModelIndex, value, role: int = Qt.ItemDataRole.EditRole) -> bool:
        if not index.isValid():
            return False

        course_student = self._course_student_dtos[index.row()]
        field_name = self._field_names[index.column()]

        if role == Qt.ItemDataRole.CheckStateRole and field_name == CourseStudentTableDTO.Fields.IS_ACTIVE:
            if value == Qt.CheckState.Checked or value == 2 or value is True:
                new_status = True
            else:
                new_status = False
            setattr(course_student, field_name, new_status)

            self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole, Qt.ItemDataRole.DisplayRole,
                                                 Qt.ItemDataRole.ForegroundRole])
            self.studentStatusChanged.emit(CourseStudentUpdateDTO(student_id=course_student.student_id,
                                                                  course_id=course_student.course_id,
                                                                  is_active=new_status))
            return True

        return False

    @override
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole
                   ) -> str | None:
        if orientation == Qt.Orientation.Horizontal:
            if role == Qt.ItemDataRole.DisplayRole:
                return self._headers[section]

            if role == Qt.ItemDataRole.ForegroundRole:
                return None

        return super().headerData(section, orientation, role)


class StudentTableView(PartialReactiveTableView):
    _is_final_component = True

    def __init__(self, table_model: QAbstractTableModel, parent: QWidget | None = None):
        self._sorting_column = CourseStudentTableDTO.Fields.LAST_NAME
        super().__init__(column_index_stretch=2, table_model=table_model, parent=parent)

        self._init_ui()

    @override
    def _connect_internal_signals(self) -> None:
        # To change the color on the entire row when the user toggle the active/inactive status. By default, if you
        # click on the checkbox, it only selects the checkbox, even if the selection mode is set to SelectRows
        nuitka_helpers.safe_connect(signal=self.clicked, slot=lambda index: self.selectRow(index.row()))

    @override
    def _configure_table_sorting(self) -> None:
        last_name = self.table_model.get_column_index(self._sorting_column) # type: ignore[arg-type]
        self.sortByColumn(last_name, Qt.SortOrder.AscendingOrder) # type: ignore[arg-type]
