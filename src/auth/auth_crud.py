from sqlalchemy.orm import Session
from src.db import models


def get_user_by_email(db: Session, email: str):
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()


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


def delete_user(db: Session, username: str, hashed_password: str):
    db_user = db.query(models.Usuario).filter(models.Usuario.nome == username).first()
    db.delete(db_user)
    db.commit()
    return db_user
