from typing import override

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget

from src.py_correction.core import paths
from src.py_correction.ui.components.base_components.widget_lifecycle_mixin import WidgetLifecycleMixin
from src.py_correction.ui.components.default_widgets.images import ResponsiveImageLabel
from src.py_correction.ui.components.default_widgets.labels import DefaultLabel, DefaultParagraphLabel


class InstructionBlockText(QWidget, WidgetLifecycleMixin):
    _is_final_component = True

    def __init__(self, block_title: str, first_paragraph: str, block_image_filename: str | None = None,
                 second_paragraph: str | None = None,
                 parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._block_title = block_title
        self._first_paragraph_text = first_paragraph
        self._block_image_filename = block_image_filename
        self._second_paragraph_text = second_paragraph

        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self._title_label = DefaultLabel(f"<h2>{self._block_title}</h2>",
                                         alignment_h_flag=Qt.AlignmentFlag.AlignHCenter) # type: ignore[arg-type]
        self._first_paragraph_label = DefaultParagraphLabel(text=self._first_paragraph_text,
                                                            alignment_h_flag=Qt.AlignmentFlag.AlignJustify) # type: ignore[arg-type]
        if self._block_image_filename is not None:
            self._pixmap_image_label = ResponsiveImageLabel(
                paths.INSTRUCTION_IMAGES.joinpath(self._block_image_filename))

        if self._second_paragraph_text is not None:
            self._second_paragraph_label = DefaultParagraphLabel(text=self._second_paragraph_text,
                                                                 alignment_h_flag=Qt.AlignmentFlag.AlignJustify) # type: ignore[arg-type]

    @override
    def _assemble_layout(self) -> None:
        block_layout = QVBoxLayout(self)
        block_layout.addWidget(self._title_label)
        block_layout.addWidget(self._first_paragraph_label)

        if self._block_image_filename is not None:
            block_layout.addWidget(self._pixmap_image_label)
            block_layout.addSpacing(12)

        if self._second_paragraph_text is not None:
            block_layout.addWidget(self._second_paragraph_label)

        block_layout.addSpacing(24)


class OptionsBlockText(QWidget, WidgetLifecycleMixin):
    _is_final_component = True

    def __init__(self, block_title: str, block_text: str, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._block_title = block_title
        self._block_text = block_text

        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self._title_label = DefaultLabel(f"<h2>{self._block_title}</h2>",
                                         alignment_h_flag=Qt.AlignmentFlag.AlignHCenter) # type: ignore[arg-type]
        self._text_label = DefaultParagraphLabel(text=self._block_text,
                                                 alignment_h_flag=Qt.AlignmentFlag.AlignLeft) # type: ignore[arg-type]

    @override
    def _assemble_layout(self) -> None:
        block_layout = QVBoxLayout(self)
        block_layout.addWidget(self._title_label)
        block_layout.addWidget(self._text_label)


class FAQBlockText(QWidget, WidgetLifecycleMixin):
    _is_final_component = True

    def __init__(self, block_question: str, block_answer: str, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._block_question = block_question
        self._block_answer = block_answer

        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self._question_label = DefaultLabel(text=self._block_question,
                                            alignment_h_flag=Qt.AlignmentFlag.AlignJustify) # type: ignore[arg-type]
        self._answer_label = DefaultParagraphLabel(text=self._block_answer,
                                                   alignment_h_flag=Qt.AlignmentFlag.AlignJustify) # type: ignore[arg-type]

    @override
    def _assemble_layout(self) -> None:
        block_layout = QVBoxLayout(self)
        block_layout.addWidget(self._question_label)
        block_layout.addWidget(self._answer_label)
