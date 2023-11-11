from sqlalchemy import Column, Integer, String

from database import Base


class Point(Base):
    __tablename__ = "points"

    id = Column(Integer, index=True, primary_key=True)
    address = Column(String)
    when_connected = Column(String)
    is_delivered = Column(String)
    days_passed = Column(Integer)
    approved_amount = Column(Integer)
    given_amount = Column(Integer)
