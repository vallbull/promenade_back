from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String

from database import Base


class Auth(Base):
    __tablename__ = "auth"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String)
    hashed_password = Column(String)


class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    grade = Column(String)
    address = Column(String)
    image_link = Column(String)


class Tasks(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    worker_id = Column(Integer)
    worker_name = Column(String)
    priority = Column(String)
    task_type = Column(String)
    address = Column(String)
    duration = Column(Integer)
    status = Column(String)
    order = Column(Integer)
    date = Column(Date)
    start_datetime = Column(DateTime, nullable=True)
    finish_datetime = Column(DateTime, nullable=True)
