
from typing import Generic, TypeVar
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlmodel import select
from todoApp.deps.deps import SessionDep
from todoApp.models.models import TodoCreate, TodoItem



router = APIRouter(prefix="/todos",tags=["todos"])

T=TypeVar("T")
class Response(BaseModel,Generic[T]):
    data:T


@router.get("/todos",response_model=Response[list[TodoItem]])
async def get_todos(sessiosn:SessionDep):
    todos=sessiosn.exec(select(TodoItem)).all()
    return Response(data=todos)


@router.get("/todos/{id}",response_model=Response[TodoItem])
async def get_todo(id:int,session:SessionDep):
    todo=session.get(TodoItem,id)
    if not todo:
        raise HTTPException(status_code=404,detail="Todo not found")
    return Response(data=todo)

@router.post("/todos",response_model=Response[TodoItem],status_code=201)
async def create_todo(session:SessionDep,todo:TodoCreate):
    db_todo=TodoItem.model_validate(todo)
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)
    return Response(data=db_todo)

@router.put("/todos/{id}",response_model=Response[TodoItem])
async def update_todo(id:int,todo:TodoCreate,session:SessionDep):
    _todo=session.get(TodoItem,id)
    if not _todo:
        raise HTTPException(status_code=404,detail="Todo not found")
    _todo.title=todo.title
    _todo.description=todo.description
    _todo.completed=todo.completed
    _todo.due_date=todo.due_date
    session.add(_todo)
    session.commit()            
    session.refresh(_todo)
    return Response(data=_todo)  


@router.delete("/todos/{id}",status_code=204)
async def delete_todo(id:int,session:SessionDep):
    todo=session.get(TodoItem,id)
    if not todo:
        raise HTTPException(status_code=404,detail="Todo not found")
    session.delete(todo)
    session.commit()


