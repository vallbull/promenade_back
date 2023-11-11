import bcrypt
from sqlalchemy.orm import Session

import models
import schemas


def check_password(password: str, hash: str):
    password_bytes = password.encode("utf-8")
    hash_bytes = hash.encode("utf-8")
    result = bcrypt.checkpw(password_bytes, hash_bytes)

    return result


def auth(db: Session, user: schemas.AuthData):
    id = None
    manager: models.ManagerAuth = (
        db.query(models.ManagerAuth).filter(models.ManagerAuth.login == user.login).first()
    )
    if manager:
        is_ok = check_password(user.password, manager.hashed_password)
        if is_ok:
            id = manager.id

    return manager, id


def get_user_by_id(db: Session, id: int):
    return db.query(models.Manager).filter(models.Manager.id == id).first()
