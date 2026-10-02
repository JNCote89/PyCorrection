from typing import override

from PySide6.QtCore import QAbstractItemModel, QEvent, QModelIndex, QObject, QPersistentModelIndex, QSize, QTimer, Qt
from PySide6.QtGui import QFontMetrics, QKeyEvent, QPainter, QPen
from PySide6.QtWidgets import (QApplication, QComboBox, QStyle, QStyleOption, QStyleOptionComboBox,
                               QStyleOptionViewItem, QStyledItemDelegate, QWidget)

from src.py_correction.ui.components.default_widgets.delegates.item_delegates import ItemDelegateStyle


class AutoResizingComboBox(QComboBox):

    def showPopup(self):
        font_metric = self.fontMetrics()
        max_width = 0
        for i in range(self.count()):
            max_width = max(max_width, font_metric.horizontalAdvance(self.itemText(i)))

        required_width = max_width + 60

        popup_container = self.view().parentWidget()
        if popup_container and required_width > self.width():
            popup_container.setMinimumWidth(required_width)

        super().showPopup()


class ComboBoxDelegate(QStyledItemDelegate):

    def __init__(self, items: list[str], placeholder_text: str, delegate_style: ItemDelegateStyle | None,
                 padding: int = 6, font_size: int = 10, parent=None):
        super().__init__(parent)
        self._items = items
        self._placeholder = placeholder_text
        self._padding = padding
        self._font_size = font_size
        self._delegate_style = delegate_style or ItemDelegateStyle(background_colors={},
                                                                   border_colors={},
                                                                   border_weight={})

    @override
    def eventFilter(self, editor: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.KeyPress:
            assert isinstance(event, QKeyEvent)

            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self.commitData.emit(editor)
                self.closeEditor.emit(editor, QStyledItemDelegate.EndEditHint.SubmitModelCache)
                return True

            elif event.key() == Qt.Key.Key_Escape:
                self.closeEditor.emit(editor, QStyledItemDelegate.EndEditHint.NoHint)
                return True

        return super().eventFilter(editor, event)

    @override
    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QPersistentModelIndex | QModelIndex
                     ) -> AutoResizingComboBox:
        editor = AutoResizingComboBox(parent)
        editor.setStyleSheet(f"QComboBox, QComboBox QAbstractItemView {{ font-size: {self._font_size}pt; }}")

        editor.addItems(self._items)

        QTimer.singleShot(0, editor.showPopup)
        return editor

    @override
    def setEditorData(self, editor: QWidget, index: QPersistentModelIndex | QModelIndex) -> None:
        if not isinstance(editor, QComboBox):
            return

        current_value = index.data(Qt.ItemDataRole.EditRole)
        idx = editor.findText(str(current_value))
        if idx >= 0:
            editor.setCurrentIndex(idx)

    @override
    def setModelData(self, editor: QWidget, model: QAbstractItemModel,
                     index: QPersistentModelIndex | QModelIndex) -> None:
        if not isinstance(editor, QComboBox):
            return

        value = editor.currentText()
        model.setData(index, value, Qt.ItemDataRole.EditRole)

    @override
    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex,
              ) -> None:

        font = option.font
        font.setPointSize(self._font_size)
        painter.setFont(font)

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True) # type: ignore[arg-type]

        value = index.data(Qt.ItemDataRole.DisplayRole)
        if value is None or value == "":
            value = index.data(Qt.ItemDataRole.EditRole)

        text = str(value).strip() if (value is not None and str(value).strip() != "") else self._placeholder

        style = option.widget.style() if option.widget else QApplication.style()

        background_color = self._delegate_style.background_colors.get(text, option.palette.base().color())
        border_color = self._delegate_style.border_colors.get(text, option.palette.mid().color())

        if option.state & QStyle.StateFlag.State_Selected and text not in self._delegate_style.background_colors:
            background_color = option.palette.highlight().color()

        cell_rect = option.rect.adjusted(1, 1, -1, -1)
        painter.setBrush(background_color)
        painter.setPen(QPen(border_color, self._delegate_style.border_weight.get(text, 1)))
        painter.drawRoundedRect(cell_rect, 3, 3)

        combo_option = QStyleOptionComboBox()
        if option.widget:
            combo_option.initFrom(option.widget)
        else:
            combo_option.palette = option.palette

        combo_option.rect = option.rect
        combo_option.fontMetrics = QFontMetrics(font)
        combo_option.state |= QStyle.StateFlag.State_Enabled | QStyle.StateFlag.State_Active # type: ignore[arg-type]

        arrow_rect = style.subControlRect(QStyle.ComplexControl.CC_ComboBox, combo_option, # type: ignore[arg-type]
                                          QStyle.SubControl.SC_ComboBoxArrow, option.widget) # type: ignore[arg-type]

        arrow_option = QStyleOption(0)
        if option.widget:
            arrow_option.initFrom(option.widget)
        else:
            arrow_option.palette = option.palette

        arrow_option.rect = arrow_rect
        arrow_option.state |= QStyle.StateFlag.State_Enabled | QStyle.StateFlag.State_Active # type: ignore[arg-type]

        style.drawPrimitive(QStyle.PrimitiveElement.PE_IndicatorArrowDown, arrow_option, painter, option.widget) # type: ignore[arg-type]

        text_rect = option.rect.adjusted(self._padding, 0, -arrow_rect.width() - self._padding, 0)
        text_flags = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft | Qt.TextFlag.TextWordWrap
        text_color = (option.palette.highlightedText().color() if
                      (option.state & QStyle.StateFlag.State_Selected and text not in
                       self._delegate_style.background_colors) else option.palette.text().color())

        painter.setPen(text_color)
        painter.drawText(text_rect, text_flags, text)

        painter.restore()

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QSize:
        size = super().sizeHint(option, index)
        value = index.data(Qt.ItemDataRole.DisplayRole)
        text = str(value) if value else self._placeholder

        font_metric = option.fontMetrics
        target_width = option.rect.width() - (self._padding * 2) - 25

        if target_width > 0:
            bounding_rect = font_metric.boundingRect(0, 0, target_width, 1000, Qt.TextFlag.TextWordWrap, text, )
            size.setHeight(max(size.height(), bounding_rect.height() + 10))

        return size
