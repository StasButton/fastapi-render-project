from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import get_db
from .models import Base

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "message": "FastAPI on Render"}

# Создаём таблицы при старте (для тестов; в проде лучше миграции)
@app.on_event("startup")
def on_startup():
    from .database import engine
    Base.metadata.create_all(bind=engine)