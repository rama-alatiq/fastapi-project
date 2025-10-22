import os
from sqlalchemy import NullPool
from sqlmodel import SQLModel, Session, create_engine


# sqlite_file_name="todo_database.db"
# sqlite_url=f"sqlite:///{sqlite_file_name}"
# connect_args={"check_same_thread":False}
# engine=create_engine(sqlite_url,connect_args=connect_args)

database_url=os.environ.get(
    "DATABASE_URL", 
    "sqlite:///./fallback.db" 
)
engine=create_engine(
    database_url,
    echo=False,
    poolclass=NullPool
)

def create_db_and_table():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session 