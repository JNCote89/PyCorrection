class ApplicationError(Exception):
    pass

class DatabaseError(ApplicationError):
    pass