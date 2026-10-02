from dataclasses import dataclass
from enum import Enum
from typing import Type

from src.py_correction.ui.components.base_components.base_page import BasePage
from src.py_correction.ui.pages.archive.archive_page import ArchivePage
from src.py_correction.ui.pages.configuration.configuration_page import ConfigurationPage
from src.py_correction.ui.pages.course.course_page import CoursePage
from src.py_correction.ui.pages.evaluation.evaluation_page import EvaluationPage
from src.py_correction.ui.pages.grade.grade_page import GradePage
from src.py_correction.ui.pages.instruction.instruction_page import InstructionPage
from src.py_correction.ui.pages.reference.reference_page import ReferencePage
from src.py_correction.ui.pages.student.student_page import StudentPage
from src.py_correction.ui.pages.submission.submission_page import SubmissionPage


@dataclass(frozen=True)
class PageConfiguration:
    widget_class: Type[BasePage]
    label: str


class PageRegistry(Enum):
    instruction = PageConfiguration(widget_class=InstructionPage,
                                    label="À propos et instructions")
    configuration = PageConfiguration(widget_class=ConfigurationPage,
                                      label="Configurations")
    course = PageConfiguration(widget_class=CoursePage,
                               label="1. Création de cours")
    evaluation = PageConfiguration(widget_class=EvaluationPage,
                                   label="2. Gestion des évaluations")
    student = PageConfiguration(widget_class=StudentPage,
                                label="3. Gestion des étudiants")
    submission = PageConfiguration(widget_class=SubmissionPage,
                                   label="4. Gestion des remises étudiantes")
    reference = PageConfiguration(widget_class=ReferencePage,
                                  label="5. Correction et vérification des références")
    grade = PageConfiguration(widget_class=GradePage,
                              label="6. Gestion des notes")
    archive = PageConfiguration(widget_class=ArchivePage,
                                label="Archivage et suppression")

    @property
    def widget_class(self) -> Type[BasePage]:
        return self.value.widget_class

    @property
    def label(self) -> str:
        return self.value.label

    @classmethod
    def from_label(cls, label_string: str | None) -> "PageRegistry | None":
        for member in cls:
            if member.label == label_string:
                return member
        return None
