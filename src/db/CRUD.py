
from sqlalchemy.orm import Session
from src.db import models

def get_user_by_username(db: Session, username: str):
    return db.query(models.Usuario).filter(models.Usuario.nome == username).first()

def get_hashed_password_by_user(db: Session, senha_hash: str):
    return db.query(models.Usuario).filter(models.Usuario.senha_hash == senha_hash).first()

def create_user(db: Session, username: str, hashed_password: str):
    db_user = models.Usuario(nome=username, senha_hash=hashed_password, cargo="user", email=f"{username}@example.com")
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, username: str, hashed_password: str):
    db_user = db.query(models.Usuario).filter(models.Usuario.nome == username).first()
    db.delete(db_user)
    db.commit()
    return db_user
