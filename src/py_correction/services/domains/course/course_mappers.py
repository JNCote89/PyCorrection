from src.py_correction.core.domains.course.course_dtos import (CourseCreateDTO, CourseResponseDTO, CourseSelectionWidgetDTO,
                                                               CourseTableDTO)
from src.py_correction.database.course.models.course_orm import CourseORM


def to_course_orm(course_input_dto: CourseCreateDTO) -> CourseORM:
    return CourseORM(semester=course_input_dto.semester,  # type: ignore
                     code=course_input_dto.code,  # type: ignore
                     name=course_input_dto.name,  # type: ignore
                     group=course_input_dto.group,  # type: ignore
                     genote_filename=course_input_dto.genote_filename,  # type: ignore
                     import_type=course_input_dto.import_type,  # type: ignore
                     creation_date=course_input_dto.creation_date)  # type: ignore


def to_course_response_dto(course_orm: CourseORM) -> CourseResponseDTO:
    return CourseResponseDTO(id=course_orm.id, semester=course_orm.semester, code=course_orm.code,
                             name=course_orm.name, group=course_orm.group, import_type=course_orm.import_type,
                             creation_date=course_orm.creation_date)


def to_course_table_dto(course_orm: CourseORM) -> CourseTableDTO:
    return CourseTableDTO(semester=course_orm.semester,
                          code=course_orm.code,
                          name=course_orm.name,
                          group=course_orm.group,
                          import_type=course_orm.import_type,
                          creation_date=course_orm.creation_date)


def to_course_selection_dto(course_orm: CourseORM) -> CourseSelectionWidgetDTO:
    return CourseSelectionWidgetDTO(id=course_orm.id,
                                    semester=course_orm.semester,
                                    code=course_orm.code,
                                    group=course_orm.group,
                                    name=course_orm.name)
