
from datetime import datetime, timezone
from typing import Any
from pydantic import ConfigDict
from sqlmodel import Field, SQLModel # type: ignore


class TodoItem(SQLModel,table=True):
    id: int | None=Field(default=None, primary_key=True)
    title: str =Field(index=True)
    completed: bool=Field(default=False)
    description:str |None=Field(default=None)
    due_date:datetime| None=Field(default=None,index=True)
    created_at:datetime=Field(default_factory=lambda:datetime.now(timezone.utc),index=True)
    model_config:Any = ConfigDict(
    json_schema_extra = {
        "propertyOrdering": [
            "id",
            "title",
            "description",
            "due_date",
            "completed",
            "created_at",
        ]
       }
    )


class TodoCreate(SQLModel):
    title:str
    description:str|None=None
    completed: bool=Field(default=False)
    due_date:datetime|None=Field(default=None)
    created_at:datetime=Field(default_factory=lambda:datetime.now(timezone.utc),index=True)

    model_config:Any = ConfigDict(
        json_schema_extra = {
            "propertyOrdering": [
                "id",
                "title",
                "description",
                "due_date",
                "completed",
                "created_at",
            ]
        }
    )

