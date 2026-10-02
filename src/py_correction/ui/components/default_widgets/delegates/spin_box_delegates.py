from typing import override

from PySide6.QtCore import QAbstractItemModel, QModelIndex, QPersistentModelIndex, QRect, Qt
from PySide6.QtGui import QPainter, QPen, QValidator
from PySide6.QtWidgets import (QApplication, QSpinBox, QStyle, QStyleOption, QStyleOptionViewItem, QStyledItemDelegate,
                               QWidget)

from src.py_correction.core.domains.shared.shared_enums import NOT_AVAILABLE
from src.py_correction.ui.components.default_widgets.delegates.item_delegates import ItemDelegateStyle

YEAR_SENTINEL_VALUE = -1


class YearSpinBox(QSpinBox):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(YEAR_SENTINEL_VALUE, 2100)
        self.minimum_year_range = 1900
        self.maximum_year_range = 2100

        self.setSpecialValueText(NOT_AVAILABLE)
        self.setSingleStep(1)

    def stepBy(self, steps: int) -> None:
        current_val = self.value()

        if steps > 0 and (current_val == -1 or not self.lineEdit().text().strip()):
            self.setValue(self.minimum_year_range)
            return

        if steps < 0 and current_val == self.minimum_year_range:
            self.setValue(YEAR_SENTINEL_VALUE)
            return

        super().stepBy(steps)

    def validate(self, input_str: str, pos: int) -> tuple[QValidator.State, str, int]:
        clean_str = input_str.strip().upper()

        if clean_str == "":
            return QValidator.State.Acceptable, input_str, pos # type: ignore[arg-type]

        if clean_str and NOT_AVAILABLE.upper().startswith(clean_str.upper()):
            return QValidator.State.Acceptable, input_str, pos # type: ignore[arg-type]

        if clean_str.isdigit():
            val = int(clean_str)

            if self.minimum_year_range <= val <= self.maximum_year_range:
                return QValidator.State.Acceptable, input_str, pos # type: ignore[arg-type]

            if len(clean_str) < 4:
                return QValidator.State.Intermediate, input_str, pos # type: ignore[arg-type]

        return QValidator.State.Invalid, input_str, pos # type: ignore[arg-type]

    def valueFromText(self, text: str) -> int:
        clean_str = text.strip().upper()

        if clean_str == "" or clean_str == NOT_AVAILABLE:
            return self.minimum()

        try:
            val = int(text)

            if self.minimum_year_range <= val <= self.maximum_year_range:
                return val

            return self.minimum()

        except ValueError:
            return self.minimum()

    def textFromValue(self, val: int) -> str:
        if val == self.minimum():
            return NOT_AVAILABLE

        return super().textFromValue(val)


class YearSpinBoxDelegate(QStyledItemDelegate):

    def __init__(self, placeholder_text: str, delegate_style: ItemDelegateStyle | None = None, font_size: int = 10,
                 padding: int = 6, parent=None):
        super().__init__(parent)
        self._font_size = font_size
        self._padding = padding
        self._delegate_style = delegate_style or ItemDelegateStyle(background_colors={},
                                                                   border_colors={},
                                                                   border_weight={})
        self._placeholder = placeholder_text

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex
                     ) -> YearSpinBox:
        editor = YearSpinBox(parent)
        editor.setStyleSheet(f"QSpinBox {{font-size: {self._font_size}pt;}}")
        return editor

    def setEditorData(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None:
        if isinstance(editor, YearSpinBox):
            value = index.data(Qt.ItemDataRole.EditRole)

            if value is None:
                editor.lineEdit().clear()
            elif str(value).strip().upper() == NOT_AVAILABLE or value == YEAR_SENTINEL_VALUE:
                editor.setValue(editor.minimum())
                editor.lineEdit().selectAll()
            else:
                try:
                    val = int(value)
                    if editor.minimum_year_range <= val <= editor.maximum_year_range:
                        editor.setValue(val)
                    else:
                        editor.setValue(editor.minimum())
                    editor.lineEdit().selectAll()
                except ValueError:
                    editor.setValue(editor.minimum())

    def setModelData(self, editor: QWidget, model: QAbstractItemModel,
                     index: QModelIndex | QPersistentModelIndex) -> None:

        if isinstance(editor, YearSpinBox):
            text = editor.lineEdit().text().strip().upper()

            if text == "":
                model.setData(index, None, Qt.ItemDataRole.EditRole)

            elif text == NOT_AVAILABLE or editor.value() == editor.minimum():
                model.setData(index, NOT_AVAILABLE, Qt.ItemDataRole.EditRole)

            else:
                model.setData(index, editor.value(), Qt.ItemDataRole.EditRole)

    def updateEditorGeometry(self, editor: QWidget, option: QStyleOptionViewItem,
                             index: QModelIndex | QPersistentModelIndex) -> None:
        rect = option.rect

        # Required to avoid the SpinBox spanning across all the cell and introducing selection bugs.
        desired_height = editor.sizeHint().height()

        if rect.height() > desired_height:
            y = rect.y() + (rect.height() - desired_height) // 2
            editor.setGeometry(QRect(rect.x(), y, rect.width(), desired_height))
        else:
            editor.setGeometry(rect)

    @override
    def paint(self, painter: QPainter, option: QStyleOptionViewItem,
              index: QModelIndex | QPersistentModelIndex) -> None:
        font = option.font
        font.setPointSize(self._font_size)
        painter.setFont(font)

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True) # type: ignore[arg-type]

        value = index.data(Qt.ItemDataRole.DisplayRole)
        if value is None or value == "":
            value = index.data(Qt.ItemDataRole.EditRole)

        if value is None or str(value).strip() == "":
            text = self._placeholder
        elif str(value).strip().upper() == NOT_AVAILABLE or value == YEAR_SENTINEL_VALUE:
            text = NOT_AVAILABLE
        else:
            text = str(value).strip()

        style = option.widget.style() if option.widget else QApplication.style()

        background_color = self._delegate_style.background_colors.get(text, option.palette.base().color())
        border_color = self._delegate_style.border_colors.get(text, option.palette.mid().color())

        if option.state & QStyle.StateFlag.State_Selected and text not in self._delegate_style.background_colors:
            background_color = option.palette.highlight().color()

        cell_rect = option.rect.adjusted(1, 1, -1, -1)
        painter.setBrush(background_color)
        painter.setPen(QPen(border_color, self._delegate_style.border_weight.get(text, 1)))
        painter.drawRoundedRect(cell_rect, 3, 3)

        arrow_width = 12
        arrow_height = 8
        gap = 1

        total_arrow_block_height = (arrow_height * 2) + gap
        center_y = option.rect.top() + (option.rect.height() - total_arrow_block_height) // 2
        arrow_x = option.rect.right() - arrow_width - self._padding

        up_rect = QRect(arrow_x, center_y, arrow_width, arrow_height)
        down_rect = QRect(arrow_x, center_y + arrow_height + gap, arrow_width, arrow_height)

        arrow_option = QStyleOption()

        if option.widget:
            arrow_option.initFrom(option.widget)
        arrow_option.palette = option.palette
        arrow_option.state |= QStyle.StateFlag.State_Enabled | QStyle.StateFlag.State_Active  # type: ignore[arg-type]

        arrow_option.rect = up_rect
        style.drawPrimitive(QStyle.PrimitiveElement.PE_IndicatorSpinUp, arrow_option, painter, option.widget) # type: ignore[arg-type]

        arrow_option.rect = down_rect
        style.drawPrimitive(QStyle.PrimitiveElement.PE_IndicatorSpinDown, arrow_option, painter, option.widget) # type: ignore[arg-type]

        text_right_padding = arrow_width + self._padding * 2
        text_rect = option.rect.adjusted(self._padding, 0, -text_right_padding, 0)

        text_flags = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft | Qt.TextFlag.TextWordWrap

        text_color = (option.palette.highlightedText().color() if (option.state & QStyle.StateFlag.State_Selected
                          and text not in self._delegate_style.background_colors) else option.palette.text().color())

        painter.setPen(text_color)
        painter.drawText(text_rect, text_flags, text)

        painter.restore()
