
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.auth import auth_handler
from src.auth import auth_models
from src.db import CRUD
from src.db import database

router = APIRouter()

@router.post("/register", response_model=auth_models.User)
def register(user: auth_models.User, db: Session = Depends(database.get_db)):
    db_user = CRUD.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = auth_handler.get_password_hash(user.password)
    db_user = CRUD.create_user(db=db, username=user.username, hashed_password=hashed_password)
    return db_user

@router.post("/login", response_model=auth_models.Token)
def login(user: auth_models.User, db: Session = Depends(database.get_db)):
    db_user = CRUD.get_user_by_username(db, username=user.username)
    if not db_user or not auth_handler.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = auth_handler.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
