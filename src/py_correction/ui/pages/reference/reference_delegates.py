from PySide6.QtCore import QObject
from PySide6.QtGui import QColor

from src.py_correction.core.domains.reference.reference_enums import (EvidenceLevelEnum, ReferenceTypeEnum,
                                                                      ReferenceVerificationStatusEnum,
                                                                      RelevanceLevelEnum)
from src.py_correction.ui.components.default_widgets.delegates.combo_box_delegates import ComboBoxDelegate
from src.py_correction.ui.components.default_widgets.delegates.item_delegates import ItemDelegateStyle
from src.py_correction.ui.components.default_widgets.delegates.spin_box_delegates import YearSpinBoxDelegate

NO_EVALUATION = "Non évaluée"
NO_EVALUATION_QCOLOR = QColor(155, 155, 155, 25)


class VerificationComboBoxDelegate(ComboBoxDelegate):
    ITEMS = [ReferenceVerificationStatusEnum.VALID, ReferenceVerificationStatusEnum.INVALID,
             ReferenceVerificationStatusEnum.TO_CHECK]
    PLACEHOLDER_TEXT = NO_EVALUATION
    DELEGATE_STYLE = ItemDelegateStyle(border_colors={ReferenceVerificationStatusEnum.VALID: QColor(0, 255, 0),
                                                      ReferenceVerificationStatusEnum.INVALID: QColor(255, 0, 0),
                                                      ReferenceVerificationStatusEnum.TO_CHECK: QColor(255, 165, 0)},
                                       background_colors={NO_EVALUATION: NO_EVALUATION_QCOLOR,
                                                          ReferenceVerificationStatusEnum.TO_CHECK: QColor(255, 165, 0,
                                                                                                           50)},
                                       border_weight={ReferenceVerificationStatusEnum.VALID: 2,
                                                      ReferenceVerificationStatusEnum.INVALID: 4,
                                                      ReferenceVerificationStatusEnum.TO_CHECK: 6})

    def __init__(self, parent: QObject | None = None):
        super().__init__(items=self.ITEMS, placeholder_text=self.PLACEHOLDER_TEXT, delegate_style=self.DELEGATE_STYLE,
                         parent=parent)


class EvidenceLevelComboBoxDelegate(ComboBoxDelegate):
    ITEMS = [EvidenceLevelEnum.HIGH, EvidenceLevelEnum.MODERATE, EvidenceLevelEnum.LOW, EvidenceLevelEnum.VERY_LOW,
             EvidenceLevelEnum.NO_EVIDENCE]
    PLACEHOLDER_TEXT = NO_EVALUATION
    DELEGATE_STYLE = ItemDelegateStyle(border_colors={},
                                       background_colors={NO_EVALUATION: NO_EVALUATION_QCOLOR},
                                       border_weight={})

    def __init__(self, parent: QObject | None = None):
        super().__init__(items=self.ITEMS, placeholder_text=self.PLACEHOLDER_TEXT, delegate_style=self.DELEGATE_STYLE,
                         parent=parent)


class RelevanceLevelComboBoxDelegate(ComboBoxDelegate):
    ITEMS = [RelevanceLevelEnum.RELEVANT, RelevanceLevelEnum.MISALIGNED, RelevanceLevelEnum.IRRELEVANT]
    PLACEHOLDER_TEXT = NO_EVALUATION
    DELEGATE_STYLE = ItemDelegateStyle(border_colors={},
                                       background_colors={NO_EVALUATION: NO_EVALUATION_QCOLOR},
                                       border_weight={})

    def __init__(self, parent: QObject | None = None):
        super().__init__(items=self.ITEMS, placeholder_text=self.PLACEHOLDER_TEXT, delegate_style=self.DELEGATE_STYLE,
                         parent=parent)


class ReferenceTypeComboBoxDelegate(ComboBoxDelegate):
    ITEMS = [ReferenceTypeEnum.SCIENTIFIC_PEER_REVIEW, ReferenceTypeEnum.SCIENTIFIC_NO_REVIEW, ReferenceTypeEnum.GREY]
    PLACEHOLDER_TEXT = NO_EVALUATION
    DELEGATE_STYLE = ItemDelegateStyle(border_colors={},
                                       background_colors={NO_EVALUATION: NO_EVALUATION_QCOLOR},
                                       border_weight={})

    def __init__(self, parent: QObject | None = None):
        super().__init__(items=self.ITEMS, placeholder_text=self.PLACEHOLDER_TEXT, delegate_style=self.DELEGATE_STYLE,
                         parent=parent)


class ReferenceYearSpinBoxDelegate(YearSpinBoxDelegate):
    PLACEHOLDER_TEXT = NO_EVALUATION
    DELEGATE_STYLE = None

    def __init__(self, parent: QObject | None = None):
        super().__init__(placeholder_text=self.PLACEHOLDER_TEXT, delegate_style=self.DELEGATE_STYLE,
                         parent=parent)
