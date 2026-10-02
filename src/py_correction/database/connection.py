from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker

from src.py_correction.core.logger import DEBUG_DB_MODE
from src.py_correction.core.paths import DATABASE_DIRECTORY
from src.py_correction.database.base.base_model import BaseORM

DB_FILENAME = "py_correction.sqlite"
db_path = DATABASE_DIRECTORY / DB_FILENAME

database_sql_url = URL.create("sqlite", database=str(db_path))

engine = create_engine(database_sql_url, echo=DEBUG_DB_MODE)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    BaseORM.metadata.create_all(bind=engine)
