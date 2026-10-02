from pathlib import Path
from typing import override

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QGroupBox, QSizePolicy, QSpinBox, QWidget

from src.py_correction.core.domains.shared.shared_dtos import ComboBoxPayload
from src.py_correction.core.domains.shared.shared_enums import AutofillOptions
from src.py_correction.core.settings_manager import ThemeOptions
from src.py_correction.engine.reference.csl.csl_enum import CitationStyle
from src.py_correction.ui.components.base_components.widget_lifecycle_mixin import WidgetLifecycleMixin
from src.py_correction.ui.components.default_widgets.check_boxes import DefaultCheckBox, DefaultToolTipCheckBox
from src.py_correction.ui.components.default_widgets.import_widgets import DefaultPathPickerWidget
from src.py_correction.ui.components.default_widgets.labels import DefaultLabel
from src.py_correction.ui.components.layouts import DefaultGridLayout
from src.py_correction.ui.pages.configuration.configuration_widgets import (CitationStyleComboBox,
                                                                            EvaluationAutofillComboBox, ThemeComboBox)


class ConfigurationsGroupBox(QGroupBox, WidgetLifecycleMixin):
    _is_final_component = True

    uiThemeChanged = Signal(ThemeOptions)
    userRootDirectoryChanged = Signal(Path)
    evaluationAutofillChanged = Signal(AutofillOptions)
    citationStyleChanged = Signal(CitationStyle)
    popupNotificationChanged = Signal(bool)
    manualSectionExpansionChanged = Signal(bool)

    def __init__(self, parent: QWidget | None = None):
        super().__init__("Configurations", parent=parent)
        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self._theme_combo_box = ThemeComboBox()
        # Fix a visual quirks of QComboBox not aligning with QLineEdit
        # ToDo: Find a more reliable way to align the widgets app width
        self._theme_combo_box.setProperty("class", "settings_combo_box")
        self._theme_combo_box.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # type: ignore[arg-type]

        self._user_root_directory_picker = DefaultPathPickerWidget()

        self._evaluation_autofill_combo_box = EvaluationAutofillComboBox()
        self._evaluation_autofill_combo_box.setProperty("class", "settings_combo_box")
        self._evaluation_autofill_combo_box.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed) # type: ignore[arg-type]

        self._citation_style_combo_box = CitationStyleComboBox()
        self._citation_style_combo_box.setProperty("class", "settings_combo_box")
        self._citation_style_combo_box.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed) # type: ignore[arg-type]

        self._theme_label = DefaultLabel(text="Thème visuel")
        self._user_root_directory_label = DefaultLabel(text="Répertoire racine (root directory) où sera créé le "
                                                            "répertoire PyCorrection qui contient l'ensemble des "
                                                            "fichiers pour chaque cours")
        self._evaluation_autofill_label = DefaultLabel(text="Mode de remplissage automatique pour la configuration des "
                                                            "gabarits de correction Excel")
        self._citation_style_label = DefaultLabel(text="Choisir le style de citation pour les références",
                                                  subtext="Seul le style APA 7e édition a été programmé pour le moment")

        self._pop_up_notification_label = DefaultLabel(text="Afficher les notifications explicatives dans une fenêtre "
                                                            "pop-up",
                                                       subtext="Ne désactive pas les notifications pour confirmer les "
                                                               "opérations")
        self._pop_up_notification_check_box = DefaultToolTipCheckBox(
            tool_tip_text="Toutes les notifications sont disponibles dans la console en tout temps.")

        self._expand_manual_section_label = DefaultLabel(text="Développer toutes les sections pour les opérations "
                                                              "manuelles",
                                                         subtext="Peut être ajusté individuellement pour chaque "
                                                                 "section")
        self._expand_manual_section_check_box = DefaultCheckBox()
        self._test = QSpinBox()

    @override
    def _assemble_layout(self) -> None:
        main_grid_layout = DefaultGridLayout(self)

        main_grid_layout.setColumnStretch(0, 1)
        main_grid_layout.setColumnStretch(1, 2)

        main_grid_layout.addWidget(self._theme_label, 0, 0)
        main_grid_layout.addWidget(self._theme_combo_box, 0, 1)

        main_grid_layout.addWidget(self._user_root_directory_label, 1, 0)
        main_grid_layout.addWidget(self._user_root_directory_picker, 1, 1)

        main_grid_layout.addWidget(self._evaluation_autofill_label, 2, 0)
        main_grid_layout.addWidget(self._evaluation_autofill_combo_box, 2, 1)

        main_grid_layout.addWidget(self._citation_style_label, 3, 0)
        main_grid_layout.addWidget(self._citation_style_combo_box, 3, 1)

        main_grid_layout.addWidget(self._pop_up_notification_label, 4, 0)
        main_grid_layout.addWidget(self._pop_up_notification_check_box, 4, 1)

        main_grid_layout.addWidget(self._expand_manual_section_label, 5, 0)
        main_grid_layout.addWidget(self._expand_manual_section_check_box, 5, 1)

    @override
    def _connect_downstream_signals(self) -> None:
        self._theme_combo_box.uiThemeChanged.connect(self.uiThemeChanged)
        self._user_root_directory_picker.userRootDirectoryChanged.connect(self.userRootDirectoryChanged)
        self._evaluation_autofill_combo_box.evaluationAutofillChanged.connect(self.evaluationAutofillChanged)
        self._citation_style_combo_box.citationStyleChanged.connect(self.citationStyleChanged)
        self._pop_up_notification_check_box.toggled.connect(self.popupNotificationChanged)
        self._expand_manual_section_check_box.toggled.connect(self.manualSectionExpansionChanged)

    @Slot(ComboBoxPayload)
    def populate_theme_combo_box(self, payload: ComboBoxPayload) -> None:
        self._theme_combo_box.populate_combo_box(payload=payload)

    @Slot(Path)
    def update_user_root_directory_picker(self, path: Path) -> None:
        self._user_root_directory_picker.update_path_directory(path_directory=path)

    @Slot(ComboBoxPayload)
    def populate_evaluation_autofill_combo_box(self, payload: ComboBoxPayload) -> None:
        self._evaluation_autofill_combo_box.populate_combo_box(payload=payload)

    @Slot(ComboBoxPayload)
    def populate_citation_style_combo_box(self, payload: ComboBoxPayload) -> None:
        self._citation_style_combo_box.populate_combo_box(payload=payload)

    def set_pop_up_notification_check_box_state(self, enabled: bool) -> None:
        self._pop_up_notification_check_box.set_state(enabled=enabled)

    def set_expand_manual_section_check_box_state(self, enabled: bool) -> None:
        self._expand_manual_section_check_box.set_state(enabled=enabled)
