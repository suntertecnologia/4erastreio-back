
from sqlalchemy.orm import Session
from src.db import models
from datetime import datetime

def get_user_by_email(db: Session, email: str):
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()

def create_user(db: Session, username: str, email: str, hashed_password: str):
    db_user = models.Usuario(nome=username, email=email, senha_hash=hashed_password, cargo="user", is_active=True)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_password(db: Session, user: models.Usuario, new_password_hash: str):
    user.senha_hash = new_password_hash
    db.commit()
    db.refresh(user)
    return user

def create_password_reset_token(db: Session, user_id: int, token: str, expires_at: datetime):
    db_token = models.PasswordResetToken(user_id=user_id, token=token, expires_at=expires_at)
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

def get_password_reset_token_by_token(db: Session, token: str):
    return db.query(models.PasswordResetToken).filter(models.PasswordResetToken.token == token).first()

def mark_password_reset_token_as_used(db: Session, token: models.PasswordResetToken):
    token.is_used = True
    db.commit()
    db.refresh(token)
    return token
