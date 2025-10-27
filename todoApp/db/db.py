import os
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy import NullPool


# sqlite_file_name="todo_database.db"
# sqlite_url=f"sqlite:///{sqlite_file_name}"
# connect_args={"check_same_thread":False}
# engine=create_engine(sqlite_url,connect_args=connect_args)

DATABASE_URL=os.environ.get(
    "DATABASE_URL", 
    "sqlite:///./fallback.db" 
)
engine=create_engine(
    DATABASE_URL,
    echo=False,
    #to rely on the supabase pooler
    poolclass=NullPool,
    connect_args={
        "connect_timeout":5,
        "options": "-c statement_timeout=5000 -c lock_timeout=5000"
    }
)

def create_db_and_table():
    try:
        SQLModel.metadata.create_all(engine)
        print("database created successfully")
    except Exception as e:
        print(f"Error during table creation:{e}")


def get_session():
    with Session(engine) as session:
        yield session 

if __name__ == "__main__":
    print("-" * 40)
    print("Running table creation utility...")
    if "postgresql" in DATABASE_URL:
        print(f"Connecting to Postgres at: {DATABASE_URL.split('@')[-1]}")
        create_db_and_table()
    else:
        print(f"Connecting to SQLite fallback: {DATABASE_URL}")
        create_db_and_table()
    print("-" * 40)