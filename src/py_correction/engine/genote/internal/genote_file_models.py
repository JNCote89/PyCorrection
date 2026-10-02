from dataclasses import dataclass, field
from pathlib import Path

from src.py_correction.engine.genote.internal.dtos import EvaluationInfo, StudentInfo
from src.py_correction.engine.genote.internal.genote_parsers import GeNoteGradeSheetParser


@dataclass
class GeNoteGradeFileData:
    file_path: str | Path
    filename: str = field(init=False)
    course_code: str = field(init=False)
    course_name: str = field(init=False)
    group: str = field(init=False)
    semester: str = field(init=False)
    student_list: list[StudentInfo] = field(init=False)
    evaluation_list: list[EvaluationInfo] = field(init=False)

    def __post_init__(self):
        path_object = Path(self.file_path)
        self.filename = path_object.name
        filename_stem = path_object.stem
        filename_info = filename_stem.split('-')
        self.course_code = filename_info[1][:6]
        self.group = filename_info[1][-2:]
        self.semester = filename_info[-1]

        file_data = GeNoteGradeSheetParser(file_path=self.file_path)

        self.course_name = file_data.get_course_name
        self.student_list = file_data.get_student_list
        self.evaluation_list = file_data.get_evaluation_list
