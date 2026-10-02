from typing import override

from PySide6.QtWidgets import QWidget

from src.py_correction.ui.components.base_components.base_page import BasePage
from src.py_correction.ui.components.layouts import DefaultPageVerticalScrollLayout
from src.py_correction.ui.components.shared_components.course_selection.course_selection_group_boxes import (
    CourseSelectionGroupBox)
from src.py_correction.ui.pages.evaluation.evaluation_controllers import EvaluationPageController
from src.py_correction.ui.pages.evaluation.evaluation_sections import (EvaluationFormImportCollapsibleSection,
                                                                       EvaluationManagementGroupBox,
                                                                       EvaluationTemplateImportGroupBox)


class EvaluationPage(BasePage):

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self.course_selection_group_box: CourseSelectionGroupBox
        self.evaluation_form_import_collapsible_section: EvaluationFormImportCollapsibleSection
        self.evaluation_template_import_groupbox: EvaluationTemplateImportGroupBox
        self.evaluation_management_groupbox: EvaluationManagementGroupBox

        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self.course_selection_group_box = CourseSelectionGroupBox()
        self.evaluation_form_import_collapsible_section = EvaluationFormImportCollapsibleSection()
        self.evaluation_template_import_groupbox = EvaluationTemplateImportGroupBox()
        self.evaluation_management_groupbox = EvaluationManagementGroupBox()

    @override
    def _initialize_controllers(self) -> None:
        self._page_controller = EvaluationPageController(page_view=self)

    @override
    def _assemble_layout(self) -> None:
        self.page_layout = DefaultPageVerticalScrollLayout(page_view=self,
                                                           widgets=[self.course_selection_group_box,
                                                                    self.evaluation_form_import_collapsible_section,
                                                                    self.evaluation_template_import_groupbox,
                                                                    self.evaluation_management_groupbox])

    def set_ui_state(self, enabled_page_widgets: bool) -> None:
        self.course_selection_group_box.set_state(enabled_page_widgets)

        self.evaluation_management_groupbox.setVisible(enabled_page_widgets)
        self.evaluation_form_import_collapsible_section.setVisible(enabled_page_widgets)
        self.evaluation_template_import_groupbox.setVisible(enabled_page_widgets)
