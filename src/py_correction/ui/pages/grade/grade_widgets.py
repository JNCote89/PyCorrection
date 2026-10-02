from PySide6.QtCore import Slot
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QWidget
from matplotlib.figure import Figure
import numpy as np
import qdarktheme

from src.py_correction.core.domains.reference.reference_figures_dtos import GradeReferencePlotDTO
from src.py_correction.core.theme_manager import ThemeOptions
from src.py_correction.ui.components.partial_widgets.figures import PartialFigure


class ReferenceGradePlotChart(PartialFigure):
    is_final_component = True

    def __init__(self, parent: QWidget | None = None, width=2, height=1.5, dpi=320):
        self.figure = Figure(figsize=(width, height), dpi=dpi, layout="constrained")

        super().__init__(figure=self.figure, figure_name="Distribution_notes_références", parent=parent)

        self._theme = ThemeOptions.DARK
        self._data = None

        self.axes1 = None
        self.axes2 = None

        self._draw_chart()

    @Slot(ThemeOptions)
    def set_theme(self, theme_name: ThemeOptions) -> None:
        self._theme = theme_name
        self._draw_chart()

    @Slot(GradeReferencePlotDTO)
    def load_data(self, grade_reference_plot_dto: GradeReferencePlotDTO | None) -> None:
        self._data = grade_reference_plot_dto
        self._draw_chart()

    def _draw_chart(self) -> None:
        # ToDo: Clean up the method with smaller protected methods
        self.figure.clf()

        num_bins = len(self._data.bins) if self._data and self._data.bins else 1
        calculated_width = max(3.5, num_bins * 0.1)

        self.figure.set_size_inches(calculated_width, 1.5)
        fixed_height = 2

        self.axes1 = self.figure.add_subplot(111)
        self.axes1.clear()

        palette = qdarktheme.load_palette(self._theme)
        bg_color = palette.color(QPalette.ColorRole.Window).name()
        text_color = palette.color(QPalette.ColorRole.WindowText).name()

        fig_width, fig_height = self.figure.get_size_inches()
        base_scale = min(fig_width, fig_height)

        y_label_fontsize = max(4, int(base_scale * 1)) # type: ignore
        x_label_fontsize = max(4, int(base_scale * 1)) # type: ignore
        title_fontsize = max(6, int(base_scale * 1.5)) # type: ignore
        tick_fontsize = max(4, int(base_scale * 1)) # type: ignore

        self.figure.patch.set_facecolor(bg_color)
        self.axes1.set_facecolor(bg_color)

        if self._data is None:
            for spine in self.axes1.spines.values(): # noqa
                spine.set_visible(False)
            self.axes1.set_xticks([])
            self.axes1.set_yticks([])
            self.axes1.set_facecolor(bg_color)
            self.axes1.set_title("Distribution des notes et des références",
                                 color=text_color, fontsize=title_fontsize, pad=16)
            self.axes1.text(0.5, 0.75,
                            "Les notes et les références n'ont pas été compilées.",
                            transform=self.axes1.transAxes,
                            ha='center',
                            va='bottom',
                            fontsize=4,
                            color=text_color,
                            alpha=0.9)
            self.draw()
            return

        grey_bar = self.axes1.bar(self._data.bins, self._data.grey_counts,
                                  label=self._data.grey_label, color=self._data.color_scheme[self._data.grey_label])

        scientific_no_review_bar = self.axes1.bar(self._data.bins, self._data.scientific_no_review_counts,
                                                  bottom=self._data.grey_counts,
                                                  label=self._data.scientific_no_review_label,
                                                  color=self._data.color_scheme[self._data.scientific_no_review_label])

        bottom_combined_bar = np.sum([self._data.grey_counts, self._data.scientific_no_review_counts], axis=0)

        scientific_review_bar = self.axes1.bar(self._data.bins, self._data.scientific_review_counts,
                                               bottom=bottom_combined_bar,
                                               label=self._data.scientific_review_label,
                                               color=self._data.color_scheme[self._data.scientific_review_label])

        self.axes1.set_xticks(self._data.bins)
        self.axes1.set_xticklabels(self._data.bins, rotation=45, ha='right')
        self.axes1.set_xlim(-1, len(self._data.bins))
        self.axes1.set_ylim(0, 150)

        self.axes2 = self.axes1.twinx()
        self.axes2.scatter(self._data.bins, self._data.grades, s=0.5, color='red', label=self._data.grade_label,
                           clip_on=False)
        self.axes2.set_ylim(0, 100)

        for spine in self.axes1.spines.values(): # noqa
            spine.set_linewidth(0.1)

        self.axes1.spines['top'].set_visible(False)
        self.axes1.spines['right'].set_visible(False)
        self.axes1.spines['left'].set_visible(True)
        self.axes1.spines['bottom'].set_visible(True)

        for spine in self.axes2.spines.values(): # noqa
            spine.set_linewidth(0.1)

        self.axes2.spines['top'].set_visible(False)
        self.axes2.spines['right'].set_visible(True)
        self.axes2.spines['left'].set_visible(False)
        self.axes2.spines['bottom'].set_visible(True)

        lines_1, labels_1 = self.axes1.get_legend_handles_labels()
        lines_2, labels_2 = self.axes2.get_legend_handles_labels()

        legend = self.axes1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='lower center',
                                   bbox_to_anchor=(0.5, 0.95), ncol=4, columnspacing=0.5,
                                   handlelength=0.5, handleheight=0.2, handletextpad=0.1, frameon=False,
                                   facecolor=bg_color, edgecolor=text_color)

        for patch in legend.get_patches():
            patch.set_width(4)  # type: ignore
            patch.set_height(2)  # type: ignore

        self.axes1.set_ylabel("Total des références", fontsize=y_label_fontsize, color=text_color)
        self.axes2.set_ylabel("Note (%)", fontsize=y_label_fontsize, color=text_color)

        self.axes1.tick_params(axis='x', labelsize=x_label_fontsize, colors=text_color, length=0)
        self.axes1.tick_params(axis='y', labelsize=tick_fontsize, colors=text_color, width=0.05, length=3)
        self.axes2.tick_params(axis='y', labelsize=tick_fontsize, colors=text_color, width=0.05, length=3)

        self.axes1.minorticks_on()
        self.axes1.tick_params(axis='x', which='minor', length=0)

        self.axes1.tick_params(axis='y', which='minor', length=1.5, width=0.025, color=text_color)

        self.axes2.tick_params(axis='y', which='minor', length=1.5, width=0.025, color=text_color)

        legend = self.axes1.get_legend()
        if legend:
            for text in legend.get_texts():
                text.set_fontsize(tick_fontsize)
                text.set_color(text_color)

            frame = legend.get_frame()
            frame.set_facecolor(bg_color)
            frame.set_edgecolor(text_color)

        self.axes1.set_title("Distribution des notes et des références",
                             color=text_color, fontsize=title_fontsize, pad=16)

        self.draw()

        target_width_px = int(calculated_width * self.figure.dpi)
        target_height_px = int(fixed_height * self.figure.dpi)

        self.setMinimumSize(target_width_px, target_height_px)
