from datetime import date, datetime, timedelta

import pytz
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
import schemas
import service
from cronjob.main import main
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


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    db.query(models.Auth).delete()
    db.query(models.Worker).delete()
    user1 = models.Worker(
        id=1,
        name="Дерягин Никита Владимирович",
        grade="Синьор",
        address="Краснодар, Красная, д. 139",
        image_link="some_link",
    )
    db.add(user1)
    user1 = models.Worker(
        id=2,
        name="Петрошев Валерий Павлович",
        grade="Мидл",
        address="Краснодар, Красная, д. 139",
        image_link="some_link",
    )
    db.add(user1)
    user1 = models.Worker(
        id=3,
        name="Евдокимов Давид Тихонович",
        grade="Джун",
        address="Краснодар, Красная, д. 139",
        image_link="some_link",
    )
    db.add(user1)
    user1 = models.Worker(
        id=4,
        name="Андреев Гордий Данилович",
        grade="Синьор",
        address="Краснодар, В.Н. Мачуги, 41",
        image_link="some_link",
    )
    db.add(user1)
    user1 = models.Worker(
        id=5,
        name="Иванов Адам Федорович",
        grade="Мидл",
        address="Краснодар, В.Н. Мачуги, 41",
        image_link="some_link",
    )
    db.add(user1)
    user1 = models.Worker(
        id=6,
        name="Бобылёв Ипполит Альбертович",
        grade="Джун",
        address="Краснодар, В.Н. Мачуги, 41",
        image_link="some_link",
    )
    db.add(user1)
    user1 = models.Worker(
        id=7,
        name="Беляева Евгения Антоновна",
        grade="Мидл",
        address="Краснодар, Красных Партизан, 321",
        image_link="some_link",
    )
    db.add(user1)
    user1 = models.Worker(
        id=8,
        name="Николаев Азарий Платонович",
        grade="Джун",
        address="Краснодар, Красных Партизан, 321",
        image_link="some_link",
    )
    db.add(user1)
    user1_auth = models.Auth(
        id=1234,
        login="ivanov.a.f@sovkom.bank",
        hashed_password="$2b$12$IvTUE6DHGCHkjXqMyzICwOAUzw9RfcpXqrwgfPFlEcV2/DpTR/WXu",
    )
    db.add(user1_auth)
    db.commit()
    db.close()


@app.get("/workers")
def read_root():
    return "Promenade workers service"


@app.post("/workers/login", response_model=schemas.Id)
def login(worker_auth: schemas.AuthData, db: Session = Depends(get_db)):
    user, id = service.auth(db=db, user=worker_auth)
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"User with login {worker_auth.login} not found"
        )
    elif id is None:
        raise HTTPException(status_code=404, detail=f"Incorrect password")
    return schemas.Id(id=id)


@app.get("/workers/get/{id}", response_model=schemas.Worker)
def get_worker_by_id(id: int, db: Session = Depends(get_db)):
    db_user = service.get_user_by_id(db, id=id)
    if db_user is None:
        raise HTTPException(status_code=404, detail=f"User with id {id} not found")
    db_user.kpi = 42
    return db_user


@app.get("/workers/generate_tasks", response_model=list[schemas.Tasks])
def generate_tasks(db: Session = Depends(get_db)):
    tasks_priority = {
        "Выезд на точку для стимулирования выдач": "Высокий",
        "Обучение агента": "Средний",
        "Доставка карт и материалов": "Низкий",
    }

    db_day = db.query(models.LastDayTasksGenerated).first()
    if db_day is None or date.today() != db_day.last_day:
        if db_day is not None:
            db_day.last_day = date.today()
            db.add(db_day)
            db.commit()
        else:
            db.add(models.LastDayTasksGenerated(last_day=date.today()))
            db.commit()
        ml_json = main(100)
        for id in ml_json:
            worker_id = id + 1
            tasks_arr = ml_json[id]
            for order, task in enumerate(tasks_arr):
                address, task_type, duration = task[0], task[1], task[2]
                worker = (
                    db.query(models.Worker)
                    .filter(models.Worker.id == worker_id)
                    .first()
                )
                worker_name = worker.name
                new_task = models.Tasks(
                    worker_id=worker_id,
                    worker_name=worker_name,
                    priority=tasks_priority[task_type],
                    task_type=task_type,
                    address=address,
                    duration=duration,
                    status="назначено",
                    order=order + 1,
                    date=date.today(),
                )
                db.add(new_task)
                db.commit()
    return db.query(models.Tasks).all()


@app.get("/workers/get_tasks/{id}", response_model=list[schemas.Tasks])
def get_task_by_worker_id_for_today(id: int, db: Session = Depends(get_db)):
    tasks = db.query(models.Tasks).filter(models.Tasks.worker_id == id).all()
    return tasks


@app.post("/workers/start_task")
def start_task(worker_id: int, order: int, db: Session = Depends(get_db)):
    task = (
        db.query(models.Tasks)
        .filter(models.Tasks.worker_id == worker_id, models.Tasks.order == order)
        .first()
    )
    start_time = datetime.now() + timedelta(hours=3)
    task.start_datetime = start_time
    db.add(task)
    task.status = "начато"
    db.commit()
    return {"status": "ok", "start_datetime": start_time}


@app.post("/workers/finish_task")
def finish_task(worker_id: int, order: int, db: Session = Depends(get_db)):
    task = (
        db.query(models.Tasks)
        .filter(models.Tasks.worker_id == worker_id, models.Tasks.order == order)
        .first()
    )
    finish_time = datetime.now() + timedelta(hours=3)
    task.finish_datetime = finish_time
    task.status = "закончено"
    db.add(task)
    db.commit()
    return {"status": "ok", "finish_datetime": finish_time}


@app.get("/workers/tasks_status_info")
def tasks_status_info(db: Session = Depends(get_db)):
    planned = db.query(models.Tasks).count()
    finished = db.query(models.Tasks).filter(models.Tasks.status == "закончено").count()
    return {
        "planned": planned,
        "finished": finished,
        "not_finished": planned - finished,
    }


@app.get("/workers/get_kpi_by_id/{worker_id}")
def get_kpi_by_id(worker_id: int, db: Session = Depends(get_db)):
    planned = db.query(models.Tasks).filter(models.Tasks.worker_id == worker_id).count()
    finished = (
        db.query(models.Tasks)
        .filter(models.Tasks.status == "закончено", models.Tasks.worker_id == worker_id)
        .count()
    )
    if planned == 0:
        kpi = 100
    else:
        kpi = (finished / planned) * 100
    return {
        "kpi": kpi,
        "updated": (datetime.now() + timedelta(hours=3)).strftime(
            "%I:%M%p on %B %d, %Y"
        ),
    }


@app.get("/workers/get_kpi")
def get_kpi(db: Session = Depends(get_db)):
    rez = {}
    for worker_id in range(1, 9):
        planned = (
            db.query(models.Tasks).filter(models.Tasks.worker_id == worker_id).count()
        )
        finished = (
            db.query(models.Tasks)
            .filter(
                models.Tasks.status == "закончено", models.Tasks.worker_id == worker_id
            )
            .count()
        )
        if planned == 0:
            kpi = 100
        else:
            kpi = (finished / planned) * 100
        worker = db.query(models.Tasks).filter(models.Tasks.worker_id == worker_id).first()
        if worker is not None:
            rez[
                worker.worker_name
            ] = kpi
    return rez


@app.get("/workers/get_tasks_info_by_type")
def get_kpi(db: Session = Depends(get_db)):
    rez = {}
    rez["departure_to_the_point"] = (
        db.query(models.Tasks)
        .filter(models.Tasks.task_type == "Выезд на точку для стимулирования выдач")
        .count()
    )
    rez["training"] = (
        db.query(models.Tasks)
        .filter(models.Tasks.task_type == "Обучение агента")
        .count()
    )
    rez["delivery"] = (
        db.query(models.Tasks)
        .filter(models.Tasks.task_type == "Доставка карт и материалов")
        .count()
    )
    return rez
