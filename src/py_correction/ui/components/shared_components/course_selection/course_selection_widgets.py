from enum import IntEnum
from typing import override

from PySide6.QtCore import QModelIndex, QSignalBlocker, QSortFilterProxyModel, Qt, Signal, Slot
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QComboBox, QWidget

from src.py_correction.core.domains.course.course_dtos import CourseSelectionWidgetDTO
from src.py_correction.ui.components.base_components.widget_lifecycle_mixin import WidgetLifecycleMixin
from src.py_correction.ui.components.default_widgets.delegates.item_delegates import DefaultWordWrapDelegate
from src.py_correction.ui.components.partial_widgets.combo_boxes import PartialComboBox
from src.py_correction.ui.components.payload_builders.shared_payloads import GenericSelectionComboBoxLabels
from src.py_correction.utils.list_format import semester_sorting_key


class EvaluationRole(IntEnum):
    DataObj = Qt.ItemDataRole.UserRole
    Semester = Qt.ItemDataRole.UserRole + 1
    SortingKey = Qt.ItemDataRole.UserRole + 2


class CourseSelectionComboBoxModel(QSortFilterProxyModel):
    _LABELS = GenericSelectionComboBoxLabels

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.source_model = QStandardItemModel(self)

        self.setSourceModel(self.source_model)
        self.setFilterRole(EvaluationRole.Semester)

        self.setSortRole(EvaluationRole.SortingKey)
        self.setDynamicSortFilter(True)

        self.semester_model = QStandardItemModel(self)

    def set_courses(self, course_selection_widget_dtos: list[CourseSelectionWidgetDTO]) -> None:
        # The QSortFilterProxyModel is finicky when use with beginResetModel/endResetModel
        # (e.g., double signal firing because of the cascading signal with the source model/proxy).
        # A custom signal in the course ComboBox was much more straightforward in this case.
        with QSignalBlocker(self):
            self.source_model.clear()
            self.semester_model.clear()

            unique_semesters = set()

            for course in course_selection_widget_dtos:
                display_text = f"{course.semester} : {course.code} (Gr{course.group}) - {course.name} "
                item = QStandardItem(display_text)
                item.setData(course.id, EvaluationRole.DataObj)
                item.setData(course.semester, EvaluationRole.Semester)

                sort_tuple = (semester_sorting_key(course.semester), course.code, course.group)
                item.setData(sort_tuple, EvaluationRole.SortingKey)

                self.source_model.appendRow(item)

                if course.semester not in unique_semesters:
                    unique_semesters.add(course.semester)

            sorted_semesters = sorted(unique_semesters, key=semester_sorting_key, reverse=True)
            sorted_semesters.insert(0, self._LABELS.SELECT_ALL)
            for semester in sorted_semesters:
                self.semester_model.appendRow(QStandardItem(semester))

            self.sort(0, Qt.SortOrder.DescendingOrder)  # type: ignore

    def map_from_course_id(self, course_id: int) -> int:
        for proxy_row in range(self.rowCount()):
            proxy_index = self.index(proxy_row, 0)
            stored_id = proxy_index.data(EvaluationRole.DataObj)
            if stored_id == course_id:
                return proxy_row
        return -1

    @Slot(str)
    def filter_course_by_semester(self, semester_label: str):
        if semester_label == self._LABELS.SELECT_ALL:
            self.setFilterFixedString("")
        else:
            self.setFilterFixedString(semester_label)

    @override
    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:  # noqa
        """Custom comparison logic using the data stored in EvaluationRole.SortingKey."""
        left_data = self.sourceModel().data(left, self.sortRole())
        right_data = self.sourceModel().data(right, self.sortRole())

        if left_data is None or right_data is None:
            return super().lessThan(left, right)

        return left_data < right_data


class CourseSemesterComboBox(QComboBox, WidgetLifecycleMixin):
    _is_final_component = True

    semesterLabelChanged = Signal(object)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        delegate = DefaultWordWrapDelegate(parent=self)
        self.setItemDelegate(delegate)

    @override
    def _connect_internal_signals(self) -> None:
        self.currentTextChanged.connect(self._on_text_changed)

    def synchronized_semester_label(self, semester_label: str | None):
        self._match_current_data_selection_index(current_data_selection=semester_label)

    @Slot(str)
    def _on_text_changed(self, semester: str) -> None:
        self.semesterLabelChanged.emit(semester)

    def _match_current_data_selection_index(self, current_data_selection: str | None):
        if current_data_selection is not None:
            matching_index = self.findText(current_data_selection)
            if matching_index != -1:
                self.setCurrentIndex(matching_index)

        self.setCurrentIndex(0)

    @override
    def wheelEvent(self, event) -> None:
        if self.hasFocus() and self.view().isVisible():
            super().wheelEvent(event)
        else:
            event.ignore()


class CourseIDComboBox(PartialComboBox):
    _is_final_component = True

    courseIDChanged = Signal(object)

    def __init__(self, parent: QWidget | None =None):
        super().__init__(parent=parent)
        self._init_ui()

    @override
    def _connect_internal_signals(self) -> None:
        self.currentIndexChanged.connect(self._on_index_changed)

    def update_placeholder(self, has_data: bool) -> None:
        text = "" if has_data else ("Aucun cours dans la base de données. Il faut créer un cours dans l'onglet "
                                    "Création de cours")
        self.setPlaceholderText(text)

    def synchronized_course_id(self, course_id: int | None):
        """ Synchronized all the course selection combo box across the pages. """
        proxy_model = self.model()
        if proxy_model and hasattr(proxy_model, "map_from_course_id"):
            proxy_row = proxy_model.map_from_course_id(course_id)
            if proxy_row != -1:
                self.setCurrentIndex(proxy_row)
                return

        self.setCurrentIndex(0)

    @Slot()
    @override
    def _on_index_changed(self, _index: int) -> None:
        current_index = self.currentIndex()
        if current_index < 0:
            return
        course_id = self.currentData(EvaluationRole.DataObj)
        self.courseIDChanged.emit(course_id)


