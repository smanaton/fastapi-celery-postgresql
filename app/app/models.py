from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    JSON,
    DateTime,
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

    task_uuid = Column(String)
    task_name = Column(String)
    # task_args = Column(JSON, nullable=True)
    # task_kwargs = Column(JSON, nullable=True)
    task_status = Column(String)
    task_result = Column(JSON, nullable=True)
    # task_date_done = Column(DateTime, nullable=True)
