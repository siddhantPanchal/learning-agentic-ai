from typing import Literal

from pydantic import BaseModel


class Status(BaseModel):
    status: Literal["open", "closed"] = "open"


class TodoSchema(BaseModel):
    id: int
    title: str
    status: Status


todos: list[TodoSchema] = [
    TodoSchema(id=1, title="Go to Shopping", status=Status()),
    TodoSchema(id=2, title="Go to School", status=Status()),
    TodoSchema(id=3, title="Play cricket", status=Status())
]
