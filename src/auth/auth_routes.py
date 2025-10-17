from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.auth import auth_models, auth_service
from src.db import database
from src.configs.logger_config import logger

router = APIRouter()


@router.post("/register", response_model=auth_models.UserOut)
def register(user: auth_models.UserAuth, db: Session = Depends(database.get_db)):
    logger.info(f"Attempting to register user with email: {user.email}")
    try:
        db_user = auth_service.register_user(db, user)
        logger.info(f"User with email {user.email} registered successfully.")
        return db_user
    except HTTPException as e:
        logger.warning(f"Failed to register user {user.email}: {e.detail}")
        raise e
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
    try:
        tokens = auth_service.login_user(db, user)
        logger.info(f"User with email {user.email} logged in successfully.")
        return tokens
    except HTTPException as e:
        logger.warning(f"Failed to login user {user.email}: {e.detail}")
        raise e
    except Exception as e:
        logger.error(
            f"Error logging in user with email {user.email}: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=500, detail="Internal server error during user login."
        )
