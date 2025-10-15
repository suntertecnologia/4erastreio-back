from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.auth import auth_crud, auth_handler, auth_models
from src.db import database
from src.configs.logger_config import logger

router = APIRouter()


@router.post("/register", response_model=auth_models.UserOut)
def register(user: auth_models.UserAuth, db: Session = Depends(database.get_db)):
    logger.info(f"Attempting to register user with email: {user.email}")
    db_user = auth_crud.get_user_by_email(db, email=user.email)
    if db_user:
        logger.warning(f"Email {user.email} already registered.")
        raise HTTPException(status_code=400, detail="Email already registered")
    try:
        username = user.email.split("@")[0]
        hashed_password = auth_handler.get_password_hash(user.password)
        db_user = auth_crud.create_user(
            db=db, username=username, email=user.email, hashed_password=hashed_password
        )
        logger.info(f"User with email {user.email} registered successfully.")
        return db_user
    except Exception as e:
        logger.error(
            f"Error registering user with email {user.email}: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=500, detail="Internal server error during user registration."
        )


@router.post("/login", response_model=auth_models.Token)
def login(user: auth_models.UserAuth, db: Session = Depends(database.get_db)):
    logger.info(f"Attempting to login user with email: {user.email}")
    db_user = auth_crud.get_user_by_email(db, email=user.email)
    if not db_user or not auth_handler.verify_password(
        user.password, db_user.senha_hash
    ):
        logger.warning(f"Invalid login attempt for email: {user.email}")
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    if not db_user.is_active:
        logger.warning(f"Login attempt from inactive user with email: {user.email}")
        raise HTTPException(status_code=400, detail="Inactive user")

    logger.info(f"User with email {user.email} logged in successfully.")
    access_token = auth_handler.create_access_token(data={"sub": db_user.email})
    refresh_token = auth_handler.create_refresh_token(data={"sub": db_user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }
