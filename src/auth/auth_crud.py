from sqlalchemy.orm import Session
from src.db import models


def get_user_by_email(db: Session, email: str):
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(models.Usuario).filter(models.Usuario.id == user_id).first()


def create_user(db: Session, email: str, username: str, hashed_password: str):
    db_user = models.Usuario(
        nome=username,
        senha_hash=hashed_password,
        cargo="user",
        email=email,
    )
    print(db_user)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
