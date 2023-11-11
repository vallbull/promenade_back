from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
import schemas
import service
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(docs_url='/api/docs')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    db.query(models.ManagerAuth).delete()
    db.query(models.Manager).delete()
    user1 = models.Manager(
        id=2222,
        name="Фролова Анастасия Андреевна",
        image_link="some_link",
    )
    db.add(user1)
    user1_auth = models.ManagerAuth(
        id=2222,
        login="frolova.a.e@sovkom.bank",
        hashed_password="$2b$12$ZHsndgPZCBJcAO3TvV0/FOP.djgTEUzbdWA3BZpJPrd1nRQf6LafG",
    )
    db.add(user1_auth)
    db.commit()
    db.close()


@app.get("/managers")
def read_root():
    return "Promenade managers service"


@app.post("/managers/login", response_model=schemas.Id)
def login(worker_auth: schemas.AuthData, db: Session = Depends(get_db)):
    user, id = service.auth(db=db, user=worker_auth)
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"User with login {worker_auth.login} not found"
        )
    elif id is None:
        raise HTTPException(status_code=404, detail=f"Incorrect password")
    return schemas.Id(id=id)


@app.get("/managers/get/{id}", response_model=schemas.Manager)
def get_manager_by_id(id: int, db: Session = Depends(get_db)):
    db_user = service.get_user_by_id(db, id=id)
    if db_user is None:
        raise HTTPException(status_code=404, detail=f"User with id {id} not found")
    return db_user
