from sqlalchemy.orm import Session

import models
import schemas


def get_points(db: Session):
    return db.query(models.Point).all()


def get_point_by_id(db: Session, id: int):
    return db.query(models.Point).filter(models.Point.id == id).first()


def add_point(db: Session, point: schemas.Point):
    db_item = models.Point(**point.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_point_by_id(db: Session, id: int):
    db_item = db.query(models.Point).filter(models.Point.id == id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
    return db_item


def update_point_by_id(db: Session, id: int, point: schemas.Point):
    db_item = db.query(models.Point).filter(models.Point.id == id).first()
    if db_item:
        db.query(models.Point).filter(models.Point.id == id).update(point.model_dump(), synchronize_session='fetch')
        db.commit()
        db.flush()
        db_item = db.query(models.Point).filter(models.Point.id == point.id).first()
    return db_item


def delete_all(db: Session):
    db.query(models.Point).delete()
    db.commit()


def insert_to_db_from_df(db: Session, df, data_columns):
    for index, row in df.iterrows():
        item_from_db = get_point_by_id(db, row[data_columns[0]])
        if item_from_db:
            delete_point_by_id(db, row[data_columns[0]])
        db_item = models.Point(
            id=row[data_columns[0]],
            address=row[data_columns[1]],
            when_connected=row[data_columns[2]],
            is_delivered=row[data_columns[3]],
            days_passed=row[data_columns[4]],
            approved_amount=row[data_columns[5]],
            given_amount=row[data_columns[6]],
        )
        db.add(db_item)
    db.commit()
    return get_points(db)
