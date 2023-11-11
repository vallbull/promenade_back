import pandas as pd
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(docs_url="/api/docs")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/points")
def read_root():
    return "Promenade points service"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/points/upload_excel", response_model=list[schemas.Point])
def upload_points_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    data_columns = [
        "№ точки",
        "Адрес точки, г. Краснодар",
        "Когда подключена точка?",
        "Карты и материалы доставлены?",
        "Кол-во дней после выдачи последней карты",
        "Кол-во одобренных заявок",
        "Кол-во выданных карт",
    ]
    df = pd.read_excel(file.file.read(), sheet_name="Входные данные для анализа")
    df = df[data_columns]
    df.dropna(inplace=True, axis=0)
    data = crud.insert_to_db_from_df(db, df, data_columns)
    return data


@app.post("/points/add", response_model=schemas.Point)
def add_point(point: schemas.Point, db: Session = Depends(get_db)):
    return crud.add_point(db=db, point=point)


@app.get("/points/get", response_model=list[schemas.Point])
def get_all_points(db: Session = Depends(get_db)):
    points = crud.get_points(db)
    return points


@app.get("/points/get/{id}", response_model=schemas.Point)
def get_point_by_id(id: int, db: Session = Depends(get_db)):
    db_point = crud.get_point_by_id(db, id=id)
    if db_point is None:
        raise HTTPException(status_code=404, detail=f"Point with id {id} not found")
    return db_point


@app.delete("/points/delete/{id}", response_model=schemas.Point)
def delete_point_by_id(id: int, db: Session = Depends(get_db)):
    db_point = crud.delete_point_by_id(db, id=id)
    if db_point is None:
        raise HTTPException(status_code=404, detail=f"Point with id {id} not found")
    return db_point


@app.put("/points/update/{id}", response_model=schemas.Point)
def update_point_by_id(id: int, point: schemas.Point, db: Session = Depends(get_db)):
    db_point = crud.update_point_by_id(db=db, id=id, point=point)
    if db_point is None:
        raise HTTPException(status_code=404, detail=f"Point with id {id} not found")
    return db_point
