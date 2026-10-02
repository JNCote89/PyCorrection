"""
Import to synchronize the model modules. Child tables must be imported first.
"""
from .course.models.course_orm import CourseORM
from .course.models.course_student_orm import CourseStudentORM
from .course_path.models.course_path_orm import CoursePathORM
from .evaluation.models.evaluation_orm import EvaluationORM
from .reference.models.reference_orm import ReferenceORM
from .student.models.student_evaluation_orm import StudentEvaluationORM
from .student.models.student_orm import StudentORM
