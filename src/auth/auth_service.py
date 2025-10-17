from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.auth import auth_crud, auth_handler, auth_models


def register_user(db: Session, user: auth_models.UserAuth):
    db_user = auth_crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    username = user.email.split("@")[0]
    hashed_password = auth_handler.get_password_hash(user.password)
    db_user = auth_crud.create_user(
        db=db, username=username, email=user.email, hashed_password=hashed_password
    )
    return db_user


def login_user(db: Session, user: auth_models.UserAuth):
    db_user = auth_crud.get_user_by_email(db, email=user.email)
    if not db_user or not auth_handler.verify_password(
        user.password, db_user.senha_hash
    ):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    if not db_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token = auth_handler.create_access_token(data={"sub": db_user.email})
    refresh_token = auth_handler.create_refresh_token(data={"sub": db_user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }
