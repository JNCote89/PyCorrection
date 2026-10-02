from pathlib import Path


def get_student_name_from_moodle_directory(moodle_directory: Path) -> str:
    # Moodle file structure as -> FamilyName, FirstName_AssignmentID_assignsubmission_file_
    return moodle_directory.name.split('_')[0]


def get_unique_student_directory_count(directory: Path) -> int:
    # If a student have 2 different submissions, Moodle create 2 directories.
    if directory.exists():
        students = set()
        for sub_directory in directory.iterdir():
            if sub_directory.is_dir():
                student_name = get_student_name_from_moodle_directory(sub_directory)
                students.add(student_name)
        return len(students)
    return 0