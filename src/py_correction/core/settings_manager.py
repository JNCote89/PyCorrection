import logging
from pathlib import Path
import tomllib

from PySide6.QtCore import QObject, Slot
from platformdirs import user_documents_path
from pydantic import BaseModel, Field, ValidationError
import tomlkit
from typing_extensions import Annotated, TYPE_CHECKING

from src.py_correction.core import nuitka_helpers
from src.py_correction.core.domains.shared.shared_enums import AutofillOptions
from src.py_correction.core.paths import USER_PROFILE_DIRECTORY
from src.py_correction.core.theme_manager import ThemeOptions
from src.py_correction.engine.reference.csl.csl_enum import CitationStyle

if TYPE_CHECKING:
    from src.py_correction.core.event_bus import EventBus

logger = logging.getLogger(__name__)


class SettingsSchema(BaseModel):
    # --- UI settings ---
    ui_theme: ThemeOptions = Field(default=ThemeOptions.DARK)
    window_width: int | None = Field(default=None, ge=400)
    window_height: int | None = Field(default=None, ge=200)
    main_splitter_sizes: list[Annotated[int, Field(ge=200, le=2000)]] = Field(default_factory=lambda: [200, 1600])

    # --- User settings ---
    user_root_directory: Path = Field(default_factory=user_documents_path)
    evaluation_autofill_option: AutofillOptions = Field(default=AutofillOptions.NONE)
    citation_style: CitationStyle = Field(default=CitationStyle.APA_7th_EDITION_UDM)
    pop_up_notifications_state: bool = Field(default=True)
    manual_section_expansion_state: bool = Field(default=False)

    # --- Navigation settings ---
    page_label_selected: str | None = Field(default=None)
    course_id_selected: int | None = Field(default=None)
    semester_label_selected: str | None = Field(default=None)
    evaluation_id_selected: int | None = Field(default=None)
    student_id_selected: int | None = Field(default=None)


class SettingsManager(QObject):
    USER_SETTINGS_FILE_PATH: Path = USER_PROFILE_DIRECTORY / "user_settings.toml"

    def __init__(self, event_bus: "EventBus"):
        super().__init__()
        self.restored_settings: SettingsSchema = self._load_settings()

        self._event_bus = event_bus

        self._connect_downstream_signal()

    def save_settings_on_shutdown(self, window_width: int, window_height: int, splitter_sizes: list[int] | None,
                                  page_label_selected: str) -> None:
        self._update_window_size(window_width=window_width, window_height=window_height)
        self._update_splitter_sizes(splitter_sizes=splitter_sizes)
        self._update_page_label_selected(page_label_selected=page_label_selected)

        self._save_to_disk()

    def _load_settings(self) -> SettingsSchema:
        if self.USER_SETTINGS_FILE_PATH.exists():
            try:
                toml_file = self.USER_SETTINGS_FILE_PATH.read_text(encoding="utf-8")
                data = tomlkit.loads(toml_file)
                return SettingsSchema.model_validate(data)
            except (ValidationError, tomllib.TOMLDecodeError):
                logger.warning("Invalid config.toml. Reverting to default configuration.")
                return SettingsSchema()
        return SettingsSchema()

    def _connect_downstream_signal(self) -> None:
        # --- Save app user configurations ---
        nuitka_helpers.safe_connect(signal=self._event_bus.settings.uiThemeChanged,
                                     slot=self._update_ui_theme)
        nuitka_helpers.safe_connect(signal=self._event_bus.settings.userRootDirectoryChanged,
                                     slot=self._update_user_root_directory)
        nuitka_helpers.safe_connect(signal=self._event_bus.settings.evaluationAutofillChanged,
                                     slot=self._update_evaluation_autofill_option)

        nuitka_helpers.safe_connect(signal=self._event_bus.settings.citationStyleChanged,
                                    slot=self._update_citation_style)

        nuitka_helpers.safe_connect(signal=self._event_bus.settings.popupNotificationChanged,
                                    slot=self._update_pop_up_messages_enabled_option)
        nuitka_helpers.safe_connect(signal=self._event_bus.settings.manualSectionExpansionChanged,
                                    slot=self._update_manual_section_expanded_option)

        # --- Save selection widget navigation ---
        nuitka_helpers.safe_connect(signal=self._event_bus.selection_widget.courseIDChanged,
                                    slot=self._update_course_id_selected)
        nuitka_helpers.safe_connect(signal=self._event_bus.selection_widget.semesterLabelChanged,
                                    slot=self._update_semester_label_selected)
        nuitka_helpers.safe_connect(signal=self._event_bus.selection_widget.evaluationIDChanged,
                                    slot=self._update_evaluation_id_selected)
        nuitka_helpers.safe_connect(signal=self._event_bus.selection_widget.studentIDChanged,
                                    slot=self._update_student_id_selected)

    def _update_window_size(self, window_width: int, window_height: int) -> None:
        """ Is update during the closeEvent from the MainWindow. Not a signal to prevent race conditions bug. """
        self.restored_settings.window_width = window_width
        self.restored_settings.window_height = window_height

    def _update_splitter_sizes(self, splitter_sizes: list[int] | None) -> None:
        """ Is update during the closeEvent from the MainWindow. Not a signal to prevent race conditions bug. """
        if splitter_sizes:
            self.restored_settings.main_splitter_sizes = splitter_sizes

    def _update_page_label_selected(self, page_label_selected: str) -> None:
        """ Is update during the closeEvent from the MainWindow. Not a signal to prevent race conditions bug. """
        self.restored_settings.page_label_selected = page_label_selected

    def _save_to_disk(self) -> None:
        """ Is called only when the app shutdown to avoid excessive I/O during app operation. """
        setting_dict = self.restored_settings.model_dump(mode="json", exclude_defaults=True)
        toml_data = tomlkit.dumps(setting_dict)
        self.USER_SETTINGS_FILE_PATH.write_text(toml_data, encoding="utf-8")

    @Slot(int)
    def _update_course_id_selected(self, course_id_selected: int) -> None:
        self.restored_settings.course_id_selected = course_id_selected

    @Slot(str)
    def _update_semester_label_selected(self, semester_label_selected: str) -> None:
        self.restored_settings.semester_label_selected = semester_label_selected

    @Slot(int)
    def _update_evaluation_id_selected(self, evaluation_id_selected: int) -> None:
        self.restored_settings.evaluation_id_selected = evaluation_id_selected

    @Slot(int)
    def _update_student_id_selected(self, student_id_selected: int) -> None:
        self.restored_settings.student_id_selected = student_id_selected


    def _update_user_root_directory(self, user_root_directory) -> None:
        self.restored_settings.user_root_directory = Path(user_root_directory)

    @Slot(ThemeOptions)
    def _update_ui_theme(self, ui_theme: ThemeOptions) -> None:
        self.restored_settings.ui_theme = ui_theme

    @Slot(AutofillOptions)
    def _update_evaluation_autofill_option(self, evaluation_autofill_option: AutofillOptions) -> None:
        self.restored_settings.evaluation_autofill_option = evaluation_autofill_option

    @Slot(str)
    def _update_citation_style(self, citation_style: CitationStyle) -> None:
        self.restored_settings.citation_style = citation_style

    @Slot(bool)
    def _update_pop_up_messages_enabled_option(self, enabled: bool) -> None:
        self.restored_settings.pop_up_notifications_state = enabled

    @Slot(bool)
    def _update_manual_section_expanded_option(self, enabled: bool) -> None:
        self.restored_settings.manual_section_expansion_state = enabled


