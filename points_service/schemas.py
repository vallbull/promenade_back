from pydantic import BaseModel


class Point(BaseModel):
    id: int
    address: str
    when_connected: str
    is_delivered: str
    days_passed: int
    approved_amount: int
    given_amount: int

    class Config:
        orm_mode = True

