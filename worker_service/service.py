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
    worker: models.Auth = (
        db.query(models.Auth).filter(models.Auth.login == user.login).first()
    )
    if worker:
        is_ok = check_password(user.password, worker.hashed_password)
        if is_ok:
            id = worker.id

    return worker, id


def get_user_by_id(db: Session, id: int):
    return db.query(models.Worker).filter(models.Worker.id == id).first()
