
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.auth import auth_handler, auth_models
from src.db import CRUD, database
from src.configs.logger_config import logger

router = APIRouter()

@router.post("/register", response_model=auth_models.UserOut)

def register(user: auth_models.UserAuth, db: Session = Depends(database.get_db)):
    logger.info(f"Attempting to register user: {user.username}")
    db_user = CRUD.get_user_by_username(db, username=user.username)
    if db_user:
        logger.warning(f"Username {user.username} already registered.")
        raise HTTPException(status_code=400, detail="Username already registered")
    try:
        hashed_password = auth_handler.get_password_hash(user.password)
        db_user = CRUD.create_user(db=db, username=user.username, hashed_password=hashed_password)
        logger.info(f"User {user.username} registered successfully.")
        return db_user
    except Exception as e:
        logger.error(f"Error registering user {user.username}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during user registration.")

@router.post("/login", response_model=auth_models.Token)
def login(user: auth_models.UserAuth, db: Session = Depends(database.get_db)):
    logger.info(f"Attempting to login user: {user.username}")
    db_user = CRUD.get_user_by_username(db, username=user.username)
    if not db_user or not auth_handler.verify_password(user.password, db_user.senha_hash):
        logger.warning(f"Invalid login attempt for username: {user.username}")
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    logger.info(f"User {user.username} logged in successfully.")
    access_token = auth_handler.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
