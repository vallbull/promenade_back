from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class Id(BaseModel):
    id: int


class AuthData(BaseModel):
    login: str
    password: str

    class Config:
        orm_mode = True


class Worker(BaseModel):
    name: str
    grade: str
    address: str
    image_link: str
    kpi: int

    class Config:
        orm_mode = True


class Tasks(BaseModel):
    worker_id: int
    worker_name: str
    priority: str
    task_type: str
    address: str
    duration: int
    status: str
    order: int
    date: date
    start_datetime: Optional[datetime | None] = None
    finish_datetime: Optional[datetime | None] = None

    class Config:
        orm_mode = True
