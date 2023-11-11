from pydantic import BaseModel


class Id(BaseModel):
    id: int


class AuthData(BaseModel):
    login: str
    password: str

    class Config:
        orm_mode = True


class Manager(BaseModel):
    name: str
    image_link: str

    class Config:
        orm_mode = True
