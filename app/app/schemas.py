from pydantic import BaseModel
from enum import Enum
from typing import Union, Any, Optional, List, Dict
from datetime import datetime


class TaskType(str, Enum):
    short = "short"
    medium = "medium"
    long = "long"


class TaskBase(BaseModel):
    type: Union[None, TaskType]


class TaskIn(TaskBase):
    pass


class Task(TaskBase):
    id: int

    # Celery domain fields
    celery_task_id: str
    celery_task_status: Optional[str]  # `PENDING`, `STARTED`, `RETRY`, `FAILURE`, `SUCCESS`
    celery_task_result: Optional[Any]
    celery_task_date_done: Optional[datetime]
    # extended fields
    celery_task_name: Optional[str]
    celery_task_args: Optional[List]
    celery_task_kwargs: Optional[Dict]
    celery_task_worker: Optional[str]
    celery_task_retries: Optional[int]
    celery_task_queue: Optional[str]


    class Config:
        orm_mode = True
