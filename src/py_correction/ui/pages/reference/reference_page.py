from typing import override

from PySide6.QtWidgets import QWidget

from src.py_correction.ui.components.base_components.base_page import BasePage
from src.py_correction.ui.components.layouts import DefaultPageVerticalScrollLayout
from src.py_correction.ui.components.shared_components.course_selection.course_selection_group_boxes import (
    CourseSelectionGroupBox)
from src.py_correction.ui.pages.reference.reference_controllers import ReferencePageController
from src.py_correction.ui.pages.reference.reference_sections import (CorrectionManagementGroupBox,
                                                                     ReferenceImportGroupBox,
                                                                     ReferenceStatisticsGroupBox,
                                                                     ReferenceTableViewGroupbox)


class ReferencePage(BasePage):

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self.course_selection_group_box: CourseSelectionGroupBox
        self.correction_management_group_box: CorrectionManagementGroupBox
        self.reference_import_group_box: ReferenceImportGroupBox
        self.reference_table_view_group_box: ReferenceTableViewGroupbox
        self.reference_statistics_group_box: ReferenceStatisticsGroupBox

        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self.course_selection_group_box = CourseSelectionGroupBox()
        self.correction_management_group_box = CorrectionManagementGroupBox()
        self.reference_import_group_box = ReferenceImportGroupBox()
        self.reference_table_view_group_box = ReferenceTableViewGroupbox()
        self.reference_statistics_group_box = ReferenceStatisticsGroupBox()

    @override
    def _initialize_controllers(self) -> None:
        self._page_controller = ReferencePageController(page_view=self)

    @override
    def _assemble_layout(self) -> None:
        self.page_layout = DefaultPageVerticalScrollLayout(page_view=self, widgets=[self.course_selection_group_box,
                                                                                    self.correction_management_group_box,
                                                                                    self.reference_import_group_box,
                                                                                    self.reference_table_view_group_box,
                                                                                    self.reference_statistics_group_box])

    def set_ui_state(self, enabled_page_widgets: bool) -> None:
        self.course_selection_group_box.set_state(enabled_page_widgets)

        self.course_selection_group_box.set_state(enabled_page_widgets)
        self.correction_management_group_box.setVisible(enabled_page_widgets)
