from src.py_correction.core.domains.student.student_dtos import StudentCreateDTO
from src.py_correction.database.student.models.student_orm import StudentORM


def to_student_orm(student_input_dto: StudentCreateDTO) -> StudentORM:
    return StudentORM(cip=student_input_dto.cip,  # type: ignore
                      last_name=student_input_dto.last_name,  # type: ignore
                      first_name=student_input_dto.first_name)  # type: ignore
