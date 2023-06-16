from pydantic import BaseModel
from enum import Enum
from typing import Union, Any


class TaskType(str, Enum):
    short = "short"
    medium = "medium"
    long = "long"


class TaskBase(BaseModel):
    type: Union[None, TaskType]


class TaskIn(TaskBase):
    pass


class Task(TaskBase):
    id: str

    task_uuid: str
    task_name: Union[None, str]
    task_status: str  # `PENDING`, `STARTED`, `RETRY`, `FAILURE`, `SUCCESS`
    task_result: Union[None, Any]

    class Config:
        orm_mode = True
