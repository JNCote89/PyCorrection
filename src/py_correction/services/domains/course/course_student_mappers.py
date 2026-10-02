from src.py_correction.core.domains.course.course_student_dtos import CourseStudentTableDTO
from src.py_correction.core.domains.shared.shared_dtos import SelectionWidgetDTO
from src.py_correction.database.course.models.course_student_orm import CourseStudentORM


def to_course_student_table_dto(course_student_orm: CourseStudentORM) -> CourseStudentTableDTO:
    return CourseStudentTableDTO(student_id=course_student_orm.student_id,
                                 course_id=course_student_orm.course_id,
                                 cip=course_student_orm.student.cip,
                                 first_name=course_student_orm.student.first_name,
                                 last_name=course_student_orm.student.last_name,
                                 import_type=course_student_orm.import_type,
                                 is_active=course_student_orm.is_active)


def to_course_student_selection_dto(course_student_orm: CourseStudentORM) -> SelectionWidgetDTO:
    return SelectionWidgetDTO(id=course_student_orm.student_id,
                              label=f"{course_student_orm.student.last_name}, {course_student_orm.student.first_name}")
