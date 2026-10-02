from enum import StrEnum

UNSET = object()
NOT_AVAILABLE = "N/A"


class AppDirectories(StrEnum):
    PYCORRECTION = "PyCorrection"
    ARCHIVES = "Archives"


class ImportTypeEnum(StrEnum):
    MANUAL = "Manuel"
    GENOTE = "GeNote"


class AutofillOptions(StrEnum):
    NONE = "None"
    LAST_ENTRY = "Last entry"
    MOST_FREQUENT = "Most frequent"
