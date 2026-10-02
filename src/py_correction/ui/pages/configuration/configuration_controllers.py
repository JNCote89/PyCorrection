from pathlib import Path
from typing import TYPE_CHECKING, override

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget

from src.py_correction.core import nuitka_helpers
from src.py_correction.core.dependency_injection import container
from src.py_correction.io_operations.filesystem import check_writable_path
from src.py_correction.ui.components.base_components.base_controller import BaseController
from src.py_correction.ui.components.payload_builders import settings_payloads

if TYPE_CHECKING:
    from src.py_correction.ui.pages.configuration.configuration_page import ConfigurationPage
    from src.py_correction.ui.pages.configuration.configuration_sections import ConfigurationsGroupBox


class ConfigurationsGroupBoxController(BaseController):

    def __init__(self, section_view: "ConfigurationsGroupBox", parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._section_view = section_view

        self._settings_manager = container.settings_manager()

        self._event_bus = container.event_bus()

        self._init_controller()

    @override
    def _connect_upstream_signals(self) -> None:
        self._event_bus.settings.userRootDirectoryChanged.connect(self._section_view.update_user_root_directory_picker)

    @override
    def _connect_downstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._section_view.uiThemeChanged,
                                    slot=self._event_bus.settings.uiThemeChanged)
        nuitka_helpers.safe_connect(signal=self._section_view.evaluationAutofillChanged,
                                    slot=self._event_bus.settings.evaluationAutofillChanged)
        nuitka_helpers.safe_connect(signal=self._section_view.citationStyleChanged,
                                    slot=self._event_bus.settings.citationStyleChanged)
        nuitka_helpers.safe_connect(signal=self._section_view.popupNotificationChanged,
                                    slot=self._event_bus.settings.popupNotificationChanged)
        nuitka_helpers.safe_connect(signal=self._section_view.manualSectionExpansionChanged,
                                    slot=self._event_bus.settings.manualSectionExpansionChanged)
        nuitka_helpers.safe_connect(signal=self._section_view.userRootDirectoryChanged,
                                    slot=self._handle_user_root_directory_changed)

    @override
    def _refresh_view(self)  -> None:
        self._refresh_theme_combo_box()
        self._refresh_root_directory_picker()
        self._refresh_autofill_combo_box()
        self._refresh_citation_combo_box()
        self._refresh_notification_check_box()
        self._refresh_manual_section_check_box()

    @Slot(Path)
    def _handle_user_root_directory_changed(self, path: Path) -> None:
        valid_path = check_writable_path(path=path)
        if valid_path:
            self._event_bus.settings.userRootDirectoryChanged.emit(valid_path)

    def _refresh_theme_combo_box(self) -> None:
        current_theme = self._settings_manager.restored_settings.ui_theme
        payload = settings_payloads.get_theme_combo_box_payload(current_selection=current_theme)
        self._section_view.populate_theme_combo_box(payload=payload)

    def _refresh_root_directory_picker(self) -> None:
        user_root_directory = self._settings_manager.restored_settings.user_root_directory
        self._section_view.update_user_root_directory_picker(user_root_directory)

    def _refresh_autofill_combo_box(self) -> None:
        current_autofill_option = self._settings_manager.restored_settings.evaluation_autofill_option
        payload = settings_payloads.get_evaluation_autofill_combo_box_payload(current_selection=current_autofill_option)
        self._section_view.populate_evaluation_autofill_combo_box(payload=payload)

    def _refresh_citation_combo_box(self) -> None:
        current_citation_style = self._settings_manager.restored_settings.citation_style
        payload = settings_payloads.get_citation_style_combo_box_payload(current_selection=current_citation_style)
        self._section_view.populate_citation_style_combo_box(payload=payload)

    def _refresh_notification_check_box(self) -> None:
        check_box_state = self._settings_manager.restored_settings.pop_up_notifications_state
        self._section_view.set_pop_up_notification_check_box_state(check_box_state)

    def _refresh_manual_section_check_box(self) -> None:
        check_box_state = self._settings_manager.restored_settings.manual_section_expansion_state
        self._section_view.set_expand_manual_section_check_box_state(check_box_state)


class ConfigurationsPageController(BaseController):

    def __init__(self, page_view: "ConfigurationPage", parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._page_view = page_view

        self._configurations_controller = ConfigurationsGroupBoxController(
            section_view=self._page_view.configurations_groupbox)

        self._init_controller()
