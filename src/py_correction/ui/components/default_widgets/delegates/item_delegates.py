from dataclasses import dataclass
from typing import override

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QStyleOptionViewItem, QStyledItemDelegate


@dataclass(frozen=True, slots=True)
class ItemDelegateStyle:
    background_colors: dict[str, QColor]
    border_colors: dict[str, QColor]
    border_weight: dict[str, int]


class DefaultWordWrapDelegate(QStyledItemDelegate):

    @override
    def initStyleOption(self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None:
        super().initStyleOption(option, index)
        option.features |= option.ViewItemFeature.WrapText
        option.displayAlignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop  # type: ignore[arg-type]
