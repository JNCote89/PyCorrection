from pathlib import Path
import re
from typing import Any, override

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QObject, QPersistentModelIndex, Qt, Signal, Slot
from PySide6.QtGui import QColor, QPalette, QTextCursor, QTextOption
from PySide6.QtWidgets import QHBoxLayout, QPlainTextEdit, QPushButton, QTextEdit, QVBoxLayout, QWidget
from matplotlib.figure import Figure
import numpy as np
import qdarktheme

from src.py_correction.core import nuitka_helpers
from src.py_correction.core.domains.reference.reference_dtos import ReferenceTableDTO, ReferenceUpdateDTO
from src.py_correction.core.domains.reference.reference_figures_dtos import (EvidenceLevelPieChartDTO,
                                                                             ReferenceTypeStackedBarChartDTO)
from src.py_correction.core.domains.shared.shared_dtos import WidgetItem
from src.py_correction.core.theme_manager import ThemeOptions
from src.py_correction.ui.components.base_components.widget_lifecycle_mixin import WidgetLifecycleMixin
from src.py_correction.ui.components.default_widgets.collapsible_sections import DefaultCollapsibleSubSection
from src.py_correction.ui.components.default_widgets.labels import DefaultDynamicLabel, DefaultLabel, \
    DefaultParagraphLabel
from src.py_correction.ui.components.partial_widgets.figures import PartialFigure
from src.py_correction.ui.components.partial_widgets.import_widgets import PartialDragAndDropWidget
from src.py_correction.ui.components.partial_widgets.list_widgets import EvaluationRole, PartialFilterListWidget
from src.py_correction.ui.components.partial_widgets.table_views import PartialFixTableView
from src.py_correction.ui.pages.reference.reference_delegates import (EvidenceLevelComboBoxDelegate,
                                                                      ReferenceTypeComboBoxDelegate,
                                                                      ReferenceYearSpinBoxDelegate,
                                                                      RelevanceLevelComboBoxDelegate,
                                                                      VerificationComboBoxDelegate)

# Qt inverse the alpha channel in the hex color and take integer for alpha value up to 255 in the rgba scheme
QT_BREAKLINE_BACKGROUND_COLOR = QColor(0, 255, 0, 150)
HTML_BREAKLINE_BACKGROUND_COLOR = (f"rgba({QT_BREAKLINE_BACKGROUND_COLOR.red()},"
                                   f"{QT_BREAKLINE_BACKGROUND_COLOR.green()},"
                                   f"{QT_BREAKLINE_BACKGROUND_COLOR.blue()},"
                                   f"{QT_BREAKLINE_BACKGROUND_COLOR.alphaF():.2f})")


class BibTextImportWidget(PartialDragAndDropWidget):
    _is_final_component = True

    bibTextFilePathSubmitted = Signal(Path)

    LABEL = "ou glisser le fichier BibText (.bib) contenant la bibliographie de l'étudiant si disponible"
    EXTENSIONS = (".bib",)
    FILE_DIALOG_WINDOW_TITLE = "Sélectionner le fichier BibText (.bib)"

    def __init__(self, parent: QWidget | None = None):
        super().__init__(label=self.LABEL, extensions=self.EXTENSIONS,
                         file_dialog_window_title=self.FILE_DIALOG_WINDOW_TITLE, allow_multiple=False,
                         parent=parent)
        self._init_ui()

    @override
    def _process_import_file(self, file_path: Path) -> None:
        self.bibTextFilePathSubmitted.emit(file_path)


class ReferenceImportTextEdit(QPlainTextEdit, WidgetLifecycleMixin):
    _is_final_component = True

    referencesChanged = Signal(list)

    WORD_BREAKS = re.compile(r'[\r\n\v\f]+')

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        option = self.document().defaultTextOption()
        option.setFlags(option.flags() | QTextOption.ShowLineAndParagraphSeparators) # type: ignore[arg-type]
        self.document().setDefaultTextOption(option)
        self.setObjectName("ReferenceImportTextEdit")
        self.setPlaceholderText("Importer un fichier BibText (.bib) avec l'encadré ci-haut ou copier-coller la liste "
                                "de référence à partir d'une liste générée par Zotero à l'intérieur d'un document Word.")

    @override
    def _connect_internal_signals(self) -> None:
        self.textChanged.connect(self._handle_text_changed)

    def get_references(self) -> list[str]:
        text = self.toPlainText()
        return [ref.strip() for ref in self.WORD_BREAKS.split(text) if ref.strip()]

    @Slot()
    def _handle_text_changed(self) -> None:
        self._highlight_line_breaks()
        self.referencesChanged.emit(self.get_references())

    def _highlight_line_breaks(self) -> None:
        text = self.toPlainText()
        extra_selections = []

        for match in self.WORD_BREAKS.finditer(text):
            start, end = match.span()

            cursor = self.textCursor()
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.KeepAnchor) # type: ignore[arg-type]

            selection = QTextEdit.ExtraSelection()
            selection.cursor = cursor

            selection.format.setBackground(QT_BREAKLINE_BACKGROUND_COLOR)

            extra_selections.append(selection)

        self.setExtraSelections(extra_selections)


class CollapsibleReferenceImportInstructions(QWidget, WidgetLifecycleMixin):
    _is_final_component = True

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._collapsible_section = DefaultCollapsibleSubSection(
            title="Instruction pour vérifier les références importées")
        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self._instruction_label = DefaultParagraphLabel(
            text=f"Si vous ne disposez pas du fichier BibText (.bib), vous pouvez copier-coller les références "
                 f"dans l'encadré bleu à partir d'une liste générée par <b>Zotero</b> à l'intérieur d'un "
                 f"document <b>Word</b>. Les documents PDF brisent l'intégrité des références et nécessitent du "
                 f"travail manuel. Il en va de même pour les étudiants qui formatent manuellement les "
                 f"références à l'intérieur d'un document Word. <br>"
                 f"Pour nettoyer les références, vous devez vous assurer que chaque référence est séparée par "
                 f"le symbole suivant : "
                 f"<span style='background-color:{HTML_BREAKLINE_BACKGROUND_COLOR};'>&para;</span> <br>"
                 f"À noter que si une ligne vide apparait, ce n'est pas un problème. "
                 f"Si le symbole <span style='background-color:{HTML_BREAKLINE_BACKGROUND_COLOR};'>&para;</span>"
                 f" apparait en plein milieu d'une référence, vous devez le retirer en insérant "
                 f"votre curseur devant le symbole, puis en appuyant sur la touche supprimée (Del / Suppr) de "
                 f"votre clavier. Si au contraire deux références sont collées, vous devez les séparer avec la "
                 f"touche entrée (Enter).")

    @override
    def _assemble_layout(self) -> None:
        self._collapsible_section.add_widget(self._instruction_label)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self._collapsible_section)
        self._collapsible_section.set_expand_state(expanded=False)


class EvaluationFilterListWidget(PartialFilterListWidget):
    _is_final_component = True

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)

    def get_evaluation_filters(self) -> list[int]:
        return [self.item(i).data(EvaluationRole.EvaluationId) for i in range(self.count())
                if self.item(i).checkState() == Qt.CheckState.Checked]


class ExcludeReferenceFilterGroup(QWidget, WidgetLifecycleMixin):
    _is_final_component = True

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._collapsible_section = DefaultCollapsibleSubSection(
            title="Exclure des références déjà évaluées précédemment")

        self.check_boxes_registry = {}

        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self._explanation_label = DefaultLabel(
            text="Cocher les évaluations contenant les références à exclure, si applicable",
            alignment_h_flag=Qt.AlignmentFlag.AlignLeft) # type: ignore[arg-type]

        self._evaluation_filter_list = EvaluationFilterListWidget()

    @override
    def _assemble_layout(self) -> None:
        self._collapsible_section.add_widget(self._explanation_label)
        self._collapsible_section.add_widget(self._evaluation_filter_list)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self._collapsible_section)
        self._collapsible_section.set_expand_state(expanded=False)

    @Slot(WidgetItem)
    def update_evaluation_filter_list(self, widget_items: list[WidgetItem]) -> None:
        self._evaluation_filter_list.update_filters(widget_items=widget_items)

    def get_evaluation_filter_list(self) -> list[int]:
        return self._evaluation_filter_list.get_evaluation_filters()

    def clear_evaluation_filter_list_selection(self) -> None:
        self._evaluation_filter_list.clear_selection()


class ReferenceTableModel(QAbstractTableModel):
    referenceUpdated = Signal(ReferenceUpdateDTO)
    rowUpdated = Signal(int)

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent=parent)
        self.reference_table_dtos: list[ReferenceTableDTO] = []

        self._headers = ReferenceTableDTO.get_headers()
        self.field_names = ReferenceTableDTO.get_field_names()

    def set_references(self, reference_table_dtos: list[ReferenceTableDTO]) -> None:
        self.beginResetModel()
        self.reference_table_dtos = reference_table_dtos
        self.endResetModel()

    def update_row(self, reference_table_dto: ReferenceTableDTO) -> None:
        if reference_table_dto.reference_id is not None:
            row = self._row_for_id(reference_id=reference_table_dto.reference_id)
        else:
            row = self._row_for_reference(student_reference=reference_table_dto.student_reference)
        if row == -1:
            return

        self.reference_table_dtos[row] = reference_table_dto

        top_left = self.index(row, 0)
        bottom_right = self.index(row, self.columnCount() - 1)
        self.dataChanged.emit(top_left, bottom_right, [Qt.ItemDataRole.DisplayRole,
                                                       Qt.ItemDataRole.DecorationRole])

        self.rowUpdated.emit(row)

    def get_column_index(self, field_name: str) -> int:
        try:
            return self.field_names.index(field_name)
        except ValueError:
            return -1

    @override
    def rowCount(self, parent: QPersistentModelIndex | QModelIndex = QModelIndex()) -> int:
        return len(self.reference_table_dtos)

    @override
    def columnCount(self, parent: QPersistentModelIndex | QModelIndex = QModelIndex()) -> int:
        return len(self._headers)

    @override
    def flags(self, index: QPersistentModelIndex | QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags  # type: ignore[arg-type]

        field_name = self.field_names[index.column()]

        read_only_fields = [ReferenceTableDTO.Fields.STUDENT_REFERENCE_HTML, ReferenceTableDTO.Fields.CROSS_REFERENCE]

        base_flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable  # type: ignore[arg-type]

        if field_name in read_only_fields:
            return base_flags # type: ignore[arg-type]

        return base_flags | Qt.ItemFlag.ItemIsEditable  # type: ignore[arg-type]

    @override
    def data(self, index: QPersistentModelIndex | QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any | None:
        if not index.isValid():
            return None

        reference = self.reference_table_dtos[index.row()]
        col = index.column()
        field_name = self.field_names[col]
        current_value = getattr(reference, field_name)

        if (field_name in [ReferenceTableDTO.Fields.STUDENT_REFERENCE_HTML, ReferenceTableDTO.Fields.CROSS_REFERENCE]
                and role == Qt.ItemDataRole.DisplayRole):
            return ""

        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            return current_value

        return None

    @override
    def setData(self, index: QPersistentModelIndex | QModelIndex, value: Any,
                role: int=Qt.ItemDataRole.EditRole) -> bool:
        if not index.isValid() or role != Qt.ItemDataRole.EditRole:
            return False

        row = index.row()
        field_name = self.field_names[index.column()]
        reference = self.reference_table_dtos[row]

        setattr(reference, field_name, value)
        self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole])

        # If no ID, no need to update the database.
        if reference.reference_id is not None:
            update_dto = ReferenceUpdateDTO(reference_id=reference.reference_id)
            setattr(update_dto, field_name, value)
            self.referenceUpdated.emit(update_dto)

        return True

    @override
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> None:
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self._headers[section]  # type: ignore
        return None

    def _row_for_id(self, reference_id: int) -> int:
        for row, item in enumerate(self.reference_table_dtos):
            item_id = getattr(item, "reference_id", None)
            if item_id == reference_id:
                return row
        return -1

    def _row_for_reference(self, student_reference: str) -> int:
        for row, item in enumerate(self.reference_table_dtos):
            item_id = getattr(item, "student_reference", None)
            if item_id == student_reference:
                return row
        return -1


class ReferenceTableView(PartialFixTableView):
    _is_final_component = True

    def __init__(self, table_model: ReferenceTableModel, parent: QWidget | None = None):
        super().__init__(column_ratios=[3, 3, 1, 1, 1, 1, 1], table_model=table_model, parent=parent)
        self.table_model = table_model
        self._init_ui()

        self._create_delegates()
        self.table_model.rowUpdated.connect(self._update_label_cells)

    def _create_delegates(self) -> None:
        delegates = {ReferenceTableDTO.Fields.VERIFICATION_STATUS: VerificationComboBoxDelegate(parent=self),
                     ReferenceTableDTO.Fields.RELEVANCE: RelevanceLevelComboBoxDelegate(parent=self),
                     ReferenceTableDTO.Fields.REFERENCE_TYPE: ReferenceTypeComboBoxDelegate(parent=self),
                     ReferenceTableDTO.Fields.EVIDENCE_LEVEL: EvidenceLevelComboBoxDelegate(parent=self),
                     ReferenceTableDTO.Fields.YEAR: ReferenceYearSpinBoxDelegate(parent=self)}

        for col_idx, field_name in enumerate(self.table_model.field_names):
            if field_name in delegates:
                self.setItemDelegateForColumn(col_idx, delegates[field_name]) # type: ignore

    @override
    def setModel(self, model) -> None:
        if self.model() is not None:
            self.model().modelAboutToBeReset.disconnect(self._clear_index_widgets)
            self.model().modelReset.disconnect(self._on_model_reset)

        super().setModel(model)

        if model is not None:
            nuitka_helpers.safe_connect(signal=model.modelAboutToBeReset,slot=self._clear_index_widgets)
            nuitka_helpers.safe_connect(signal=model.modelReset, slot=self._on_model_reset)

    def _on_model_reset(self) -> None:
        self._insert_label_cells()

    def _clear_index_widgets(self) -> None:
        model = self.model()
        if not model:
            return

        for row in range(model.rowCount()):
            for col in range(model.columnCount()):
                index = model.index(row, col)
                if self.indexWidget(index) is not None:
                    # Passing None deletes the widget and frees memory
                    self.setIndexWidget(index, None) # type: ignore[arg-type]

    def _insert_label_cells(self) -> None:
        model = self.model()
        if not model:
            return

        label_column_names = [ReferenceTableDTO.Fields.STUDENT_REFERENCE_HTML, ReferenceTableDTO.Fields.CROSS_REFERENCE]

        for label_column_name in label_column_names:
            url_column_index = self.table_model.get_column_index(label_column_name)

            for row in range(self.table_model.rowCount()):
                index = self.table_model.index(row, url_column_index)
                reference = self.table_model.reference_table_dtos[row]

                citation_text = getattr(reference, label_column_name)

                label = DefaultDynamicLabel(text=citation_text or "",
                                            custom_html_style="font-size: 10pt;padding: 0px; margin: 0px;")

                self.setIndexWidget(index, label)

        self.adjust_table_height()

    @Slot(int)
    def _update_label_cells(self, row: int) -> None:
        model = self.model()
        if model is None or row < 0 or row >= model.rowCount():
            return

        label_column_names = [ReferenceTableDTO.Fields.STUDENT_REFERENCE_HTML, ReferenceTableDTO.Fields.CROSS_REFERENCE]

        reference = self.table_model.reference_table_dtos[row]

        for field_name in label_column_names:
            column = self.table_model.get_column_index(field_name)
            if column == -1:
                continue

            index = model.index(row, column)
            citation_text = getattr(reference, field_name)

            label = DefaultDynamicLabel(text=citation_text,
                                        custom_html_style="font-size: 10pt; padding: 0px; margin: 0px;")
            self.setIndexWidget(index, label)

        self.adjust_table_height()


class CollapsibleDeleteReferences(QWidget, WidgetLifecycleMixin):
    _is_final_component = True

    referenceDeletedButtonClicked = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._collapsible_section = DefaultCollapsibleSubSection(
            title="Supprimer les références à évaluer")
        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self._delete_label = DefaultLabel(
            text=f"Attention, la suppression des références est irréversible et entraîne la perte des références "
                 f"déjà évaluées pour cet étudiant.",
            alignment_h_flag=Qt.AlignmentFlag.AlignLeft) # type: ignore[arg-type]
        self._delete_button = QPushButton("Supprimer les références évaluées")
        self._delete_button.setProperty("class", "delete_button")

    @override
    def _assemble_layout(self) -> None:
        inner_section_layout = QHBoxLayout()
        inner_section_layout.addWidget(self._delete_label)
        inner_section_layout.addWidget(self._delete_button)

        self._collapsible_section.insert_layout(inner_section_layout)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self._collapsible_section)
        self._collapsible_section.set_expand_state(expanded=False)

    @override
    def _connect_downstream_signals(self) -> None:
        self._delete_button.clicked.connect(self.referenceDeletedButtonClicked)


class ReferenceTypeStackedBarChart(PartialFigure):
    is_final_component = True

    def __init__(self, parent: QWidget | None = None, width: float = 3, height: float=1.5, dpi: int = 320):
        self.figure = Figure(figsize=(width, height), dpi=dpi, layout="constrained")
        super().__init__(figure=self.figure, figure_name="Type_de_références", parent=parent)

        self._theme = ThemeOptions.DARK
        self._data = None

        self._draw_chart()

    @Slot(ThemeOptions)
    def set_theme(self, theme_name: ThemeOptions) -> None:
        self._theme = theme_name
        self._draw_chart()

    @Slot(ReferenceTypeStackedBarChartDTO)
    def load_data(self, reference_type_stacked_bar_chart_dto: ReferenceTypeStackedBarChartDTO | None) -> None:
        self._data = reference_type_stacked_bar_chart_dto
        self._draw_chart()

    def _draw_chart(self) -> None:
        # ToDo: Clean up the method with smaller protected methods
        self.figure.clf()
        self.axes = self.figure.add_subplot(111)
        self.axes.clear()

        palette = qdarktheme.load_palette(self._theme)
        bg_color = palette.color(QPalette.ColorRole.Window).name()
        text_color = palette.color(QPalette.ColorRole.WindowText).name()

        fig_width, fig_height = self.figure.get_size_inches()
        base_scale = min(fig_width, fig_height)

        label_fontsize = max(4, int(base_scale * 1)) # type: ignore
        title_fontsize = max(6, int(base_scale * 1.5)) # type: ignore
        tick_fontsize = max(4, int(base_scale * 1)) # type: ignore

        self.figure.patch.set_facecolor(bg_color)
        self.axes.set_facecolor(bg_color)

        if self._data is None:
            for spine in self.axes.spines.values(): # noqa
                spine.set_visible(False)
            self.axes.set_xticks([])
            self.axes.set_yticks([])
            self.axes.set_facecolor(bg_color)
            self.axes.set_title("Distribution par année du type de références",
                                color=text_color, fontsize=title_fontsize, pad=16)
            self.axes.text(0.5, 0.75,
                           "Le type de référence n'a pas été évalué",
                           transform=self.axes.transAxes,
                           ha='center',
                           va='bottom',
                           fontsize=4,
                           color=text_color,
                           alpha=0.9)
            self.draw()
            return

        grey_bar = self.axes.bar(self._data.bins, self._data.grey_counts,
                                 label=self._data.grey_label, color=self._data.color_scheme[self._data.grey_label])

        scientific_no_review_bar = self.axes.bar(self._data.bins, self._data.scientific_no_review_counts,
                                                 bottom=self._data.grey_counts,
                                                 label=self._data.scientific_no_review_label,
                                                 color=self._data.color_scheme[self._data.scientific_no_review_label])

        bottom_combined_bar = np.sum([self._data.grey_counts, self._data.scientific_no_review_counts], axis=0)

        scientific_review_bar = self.axes.bar(self._data.bins, self._data.scientific_review_counts,
                                              bottom=bottom_combined_bar,
                                              label=self._data.scientific_review_label,
                                              color=self._data.color_scheme[self._data.scientific_review_label])

        self.axes.set_xticks(self._data.bins)
        self.axes.set_xticklabels(self._data.bins, rotation=45, ha='right')
        self.axes.set_ylim(0, 40)

        for spine in self.axes.spines.values(): # noqa
            spine.set_linewidth(0.1)

        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        self.axes.spines['left'].set_visible(True)
        self.axes.spines['bottom'].set_visible(True)

        legend = self.axes.legend(loc='lower center', bbox_to_anchor=(0.5, 0.85), ncol=3, columnspacing=0.5,
                                  handlelength=0.5, handleheight=0.2, handletextpad=0.1, frameon=False,
                                  facecolor=bg_color, edgecolor=text_color)

        for patch in legend.get_patches():
            patch.set_width(4) # type: ignore
            patch.set_height(2) # type: ignore

        self.axes.set_xlabel("Année", fontsize=label_fontsize, color=text_color)
        self.axes.set_ylabel("Total", fontsize=label_fontsize, color=text_color)

        self.axes.tick_params(axis='x', labelsize=tick_fontsize, colors=text_color, length=0)
        self.axes.tick_params(axis='y', labelsize=tick_fontsize, colors=text_color, width=0.05, length=3)

        self.axes.minorticks_on()
        self.axes.tick_params(axis='x', which='minor', length=0)

        self.axes.tick_params(axis='y', which='minor', length=1.5, width=0.025, color=text_color)

        totals = np.sum([self._data.grey_counts, self._data.scientific_no_review_counts,
                         self._data.scientific_review_counts], axis=0)

        bar_labels = [str(int(t)) if t > 0 else "" for t in totals]

        self.axes.bar_label(scientific_review_bar, labels=bar_labels, padding=1, fontsize=tick_fontsize - 1,
                            color=text_color, fontweight='bold')

        max_total = max(totals) if len(totals) > 0 else 50
        self.axes.set_ylim(0, max(50, max_total * 1.15))

        legend = self.axes.get_legend()
        if legend:
            for text in legend.get_texts():
                text.set_fontsize(tick_fontsize)
                text.set_color(text_color)

            frame = legend.get_frame()
            frame.set_facecolor(bg_color)
            frame.set_edgecolor(text_color)

        self.axes.set_title("Distribution par année du type de références",
                            color=text_color, fontsize=title_fontsize, pad=16)

        self.draw()


class EvidenceLevelPieChart(PartialFigure):
    is_final_component = True

    def __init__(self, parent: QWidget | None = None, width=1.75, height=1.75, dpi=320):
        self.figure = Figure(figsize=(width, height), dpi=dpi, layout="constrained")
        super().__init__(figure=self.figure, figure_name="Niveau_de_preuves", parent=parent)

        self._theme = ThemeOptions.SYSTEM
        self._data = None

    @Slot(ThemeOptions)
    def set_theme(self, theme_name: ThemeOptions) -> None:
        self._theme = theme_name
        self._draw_chart()

    @Slot(EvidenceLevelPieChartDTO)
    def load_data(self, pie_chart_dto: EvidenceLevelPieChartDTO | None) -> None:
        self._data = pie_chart_dto
        self._draw_chart()

    def _draw_chart(self) -> None:
        # ToDo: Clean up the method with smaller protected methods
        self.figure.clf()
        self.axes = self.figure.add_subplot(111)

        self.axes.clear()

        palette = qdarktheme.load_palette(self._theme)
        bg_color = palette.color(QPalette.ColorRole.Window).name()
        text_color = palette.color(QPalette.ColorRole.WindowText).name()

        fig_width, fig_height = self.figure.get_size_inches()
        base_scale = min(fig_width, fig_height)

        label_fontsize = max(4, int(base_scale * 1)) # type: ignore
        title_fontsize = max(6, int(base_scale * 1.5)) # type: ignore

        self.figure.patch.set_facecolor(bg_color)
        self.axes.set_facecolor(bg_color)

        if self._data is None or not self._data.values:
            for spine in self.axes.spines.values(): # noqa
                spine.set_visible(False)
            self.axes.set_xticks([])
            self.axes.set_yticks([])
            self.axes.set_facecolor(bg_color)
            self.axes.set_title("Niveau de preuve",
                                color=text_color, fontsize=title_fontsize, pad=8)
            self.axes.text(0.5, 0.75,
                           f"Le niveau de preuve n'a pas été évalué",
                           transform=self.axes.transAxes,
                           ha='center',
                           va='bottom',
                           fontsize=4,
                           color=text_color,
                           alpha=0.9)

            self.draw()
            return

        wedges, texts, autotexts = self.axes.pie(self._data.values, labels=self._data.labels,
                                                 colors=self._data.colors, autopct="%d%%", startangle=90,
                                                 labeldistance=1.15)

        self.axes.set_aspect('equal')

        for text in texts:
            text.set_color(text_color)
            text.set_fontsize(label_fontsize)

        for autotext in autotexts:
            autotext.set_color("#FFFFFF")
            autotext.set_fontweight("bold")
            autotext.set_fontsize(label_fontsize)

        self.axes.set_title("Niveau de preuve",
                            color=text_color, fontsize=title_fontsize, pad=8)

        total_citations = np.sum(self._data.values)
        self.axes.text(0.5, 1.01,
                       f"(n = {total_citations})",
                       transform=self.axes.transAxes,
                       ha='center',
                       va='bottom',
                       fontsize=4,
                       color=text_color,
                       alpha=0.9)

        self.draw()
