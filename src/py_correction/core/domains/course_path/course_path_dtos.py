from dataclasses import dataclass, field, fields
from pathlib import Path

from src.py_correction.core.domains.shared.shared_enums import AppDirectories
from src.py_correction.core.domains.shared.shared_enums import UNSET


@dataclass
class CoursePathCreateDTO:
    user_root_directory: Path
    semester: str
    course_code: str
    group: str

    submissions_directory_name: str = "Remises étudiantes"
    grades_directory_name: str = "GeNote"
    group_directory_name: str = "Groupe - "
    correction_templates_directory_name: str = "Gabarits de correction"
    corrections_directory_name: str = "Corrections"
    submission_archives_directory_name: str = "Archives de Moodle"
    correction_archives_directory_name: str = "Fichiers pour Moodle"

    @property
    def course_root_path(self) -> Path:
        return (Path(self.user_root_directory) / AppDirectories.PYCORRECTION / self.semester / self.course_code
                / f"{self.group_directory_name}{self.group}")

    @property
    def corrections_directory(self) -> Path:
        return self.course_root_path / self.corrections_directory_name

    @property
    def correction_templates_directory(self) -> Path:
        return self.course_root_path / self.correction_templates_directory_name

    @property
    def grades_directory(self) -> Path:
        return self.course_root_path / self.grades_directory_name

    @property
    def submissions_directory(self) -> Path:
        return self.course_root_path / self.submissions_directory_name

    @property
    def submission_archives_directory(self) -> Path:
        return self.submissions_directory / self.submission_archives_directory_name

    @property
    def correction_archives_directory(self) -> Path:
        return self.corrections_directory / self.correction_archives_directory_name

    @property
    def directories(self) -> list[Path]:
        return [self.corrections_directory, self.correction_templates_directory, self.grades_directory,
                self.submissions_directory, self.submission_archives_directory, self.correction_archives_directory]


@dataclass
class GeNoteResponseDTO:
    new_source_path: Path
    grade_directory_path: Path


@dataclass
class ArchiveCoursePathResponseDTO:
    course_path_id: int
    course_id: int
    user_root_directory: Path
    course_root_path: Path
    semester: str
    course_code: str
    group: str


@dataclass
class UpdateCoursePathDTO:
    id: int = field(metadata={"updatable": False})
    course_id: int = field(metadata={"updatable": False})

    user_root_directory: Path = field(default=UNSET, metadata={"updatable": True})
    course_root_path: Path = field(default=UNSET, metadata={"updatable": True})
    corrections_directory: Path = field(default=UNSET, metadata={"updatable": True})
    correction_templates_directory: Path = field(default=UNSET, metadata={"updatable": True})
    grades_directory: Path = field(default=UNSET, metadata={"updatable": True})
    submissions_directory: Path = field(default=UNSET, metadata={"updatable": True})
    submission_archives_directory: Path = field(default=UNSET, metadata={"updatable": True})
    correction_archives_directory: Path = field(default=UNSET, metadata={"updatable": True})

    def updatable_items_to_dict(self) -> dict:
        updatable_fields = [f.name for f in fields(self) if f.metadata["updatable"] is not False]
        return {k: v for k, v in self.__dict__.items() if k in updatable_fields and v is not UNSET}
