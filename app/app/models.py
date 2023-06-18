from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    JSON,
    DateTime,
    PickleType,
    LargeBinary,
    inspect,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from typing import Dict, Any
from datetime import datetime


@as_declarative()
class Base:
    __name__: str

    def dict(self) -> Dict[str, Any]:
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Celery domain fields, ref: [Task](https://docs.celeryq.dev/en/latest/internals/reference/celery.backends.database.models.html#celery.backends.database.models.Task`)
    celery_task_id = Column(String, unique=True)
    celery_task_status = Column(
        String, default="PENDING"
    )  # `PENDING`, `STARTED`, `RETRY`, `FAILURE`, `SUCCESS`
    celery_task_result = Column(PickleType, nullable=True)
    celery_date_done = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True
    )
    # extended fields, ref: [TaskExtended](https://docs.celeryq.dev/en/latest/internals/reference/celery.backends.database.models.html#celery.backends.database.models.TaskExtended`)
    celery_task_name = Column(String, nullable=True)
    celery_task_args = Column(LargeBinary, nullable=True)
    celery_task_kwargs = Column(LargeBinary, nullable=True)
    celery_task_worker = Column(String, nullable=True)
    celery_task_retries = Column(Integer, nullable=True)
    celery_task_queue = Column(String, nullable=True)
