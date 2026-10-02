from src.py_correction.core.domains.course_path.course_path_dtos import CoursePathCreateDTO, UpdateCoursePathDTO
from src.py_correction.database.course_path.models.course_path_orm import CoursePathORM


def to_course_path_orm(dto: "CoursePathCreateDTO", course_id: int) -> CoursePathORM:
    return CoursePathORM(course_id=course_id,   # type: ignore
                         user_root_directory=dto.user_root_directory,  # type: ignore
                         course_root_path=dto.course_root_path,  # type: ignore
                         corrections_directory=dto.corrections_directory,  # type: ignore
                         correction_templates_directory=dto.correction_templates_directory,  # type: ignore
                         grades_directory=dto.grades_directory,  # type: ignore
                         submissions_directory=dto.submissions_directory,  # type: ignore
                         submission_archives_directory=dto.submission_archives_directory,  # type: ignore
                         correction_archives_directory=dto.correction_archives_directory)  # type: ignore


def to_update_course_path_dto(dto: "CoursePathCreateDTO", course_id: int,
                              course_path_id: int) -> UpdateCoursePathDTO:
    return UpdateCoursePathDTO(id=course_path_id,
                               course_id=course_id,
                               user_root_directory=dto.user_root_directory,
                               course_root_path=dto.course_root_path,
                               corrections_directory=dto.corrections_directory,
                               correction_templates_directory=dto.correction_templates_directory,
                               grades_directory=dto.grades_directory,
                               submissions_directory=dto.submissions_directory,
                               submission_archives_directory=dto.submission_archives_directory,
                               correction_archives_directory=dto.correction_archives_directory)
