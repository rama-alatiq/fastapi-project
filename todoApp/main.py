from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI
from sqlmodel import Session, select
from todoApp.db.db import create_db_and_table,engine
from todoApp.models.models import TodoItem
from todoApp.routers.todos import router as todos_router


@asynccontextmanager
async def lifespan(app:FastAPI):
    create_db_and_table()
    with Session(engine) as session:
        if not session.exec(select(TodoItem)).first():
            session.add_all([
                TodoItem(title="First Task",description="This is the first task",due_date=datetime.now()),
                TodoItem(title="Second Task",description="This is the second task",due_date=datetime.now()),
            ])
            session.commit()
            
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(router=todos_router)

@app.get("/ping")
def ping(): return {"ok": True}

