from sqlalchemy import Column, ForeignKey, Integer, String

from database import Base


class ManagerAuth(Base):
    __tablename__ = "manager_auth"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String)
    hashed_password = Column(String)


class Manager(Base):
    __tablename__ = "managers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    image_link = Column(String)
