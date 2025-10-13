
from fastapi import FastAPI
from src.auth import auth_routes
from src.db import models
from src.db.database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_routes.router, prefix="/auth")

@app.get("/")
def read_root():
    return {"message": "Welcome to the SunterCode Tracking API"}
