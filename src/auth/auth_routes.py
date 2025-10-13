
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.auth import auth_handler, auth_models
from src.db import CRUD, database
from src.configs.logger_config import logger
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/register", response_model=auth_models.UserOut)
def register(user: auth_models.UserAuth, db: Session = Depends(database.get_db)):
    logger.info(f"Attempting to register user with email: {user.email}")
    db_user = CRUD.get_user_by_email(db, email=user.email)
    if db_user:
        logger.warning(f"Email {user.email} already registered.")
        raise HTTPException(status_code=400, detail="Email already registered")
    try:
        username = user.email.split('@')[0]
        hashed_password = auth_handler.get_password_hash(user.password)
        db_user = CRUD.create_user(db=db, username=username, email=user.email, hashed_password=hashed_password)
        logger.info(f"User with email {user.email} registered successfully.")
        return db_user
    except Exception as e:
        logger.error(f"Error registering user with email {user.email}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during user registration.")

@router.post("/login", response_model=auth_models.Token)
def login(user: auth_models.UserAuth, db: Session = Depends(database.get_db)):
    logger.info(f"Attempting to login user with email: {user.email}")
    db_user = CRUD.get_user_by_email(db, email=user.email)
    if not db_user or not auth_handler.verify_password(user.password, db_user.senha_hash):
        logger.warning(f"Invalid login attempt for email: {user.email}")
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    if not db_user.is_active:
        logger.warning(f"Login attempt from inactive user with email: {user.email}")
        raise HTTPException(status_code=400, detail="Inactive user")

    logger.info(f"User with email {user.email} logged in successfully.")
    access_token = auth_handler.create_access_token(data={"sub": db_user.email})
    refresh_token = auth_handler.create_refresh_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}

@router.post("/refresh-token", response_model=auth_models.Token)
def refresh_token(refresh_token_data: auth_models.RefreshTokenRequest, db: Session = Depends(database.get_db)):
    email = auth_handler.verify_refresh_token(refresh_token_data.refresh_token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    db_user = CRUD.get_user_by_email(db, email=email)
    if not db_user:
        raise HTTPException(status_code=401, detail="User not found")

    access_token = auth_handler.create_access_token(data={"sub": db_user.email})
    refresh_token = auth_handler.create_refresh_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}

@router.post("/forgot-password")
def forgot_password(request: auth_models.ForgotPasswordRequest, db: Session = Depends(database.get_db)):
    db_user = CRUD.get_user_by_email(db, email=request.email)
    if not db_user:
        logger.warning(f"Password reset request for non-existent email: {request.email}")
        # Still return a success message to not reveal if an email is registered or not
        return {"message": "If an account with this email exists, a password reset link has been sent."}

    reset_token = auth_handler.create_password_reset_token()
    expires_at = datetime.utcnow() + timedelta(hours=24)
    CRUD.create_password_reset_token(db, user_id=db_user.id, token=reset_token, expires_at=expires_at)

    # In a real application, you would send an email here.
    # For this example, we will log the reset link.
    reset_link = f"http://localhost:8000/auth/reset-password?token={reset_token}"
    logger.info(f"Password reset link for {request.email}: {reset_link}")

    return {"message": "If an account with this email exists, a password reset link has been sent."}

@router.post("/reset-password")
def reset_password(request: auth_models.ResetPasswordRequest, db: Session = Depends(database.get_db)):
    token_data = CRUD.get_password_reset_token_by_token(db, token=request.token)

    if not token_data or token_data.is_used or token_data.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired password reset token.")

    db_user = db.query(CRUD.models.Usuario).filter(CRUD.models.Usuario.id == token_data.user_id).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid token.")

    hashed_password = auth_handler.get_password_hash(request.new_password)
    CRUD.update_user_password(db, user=db_user, new_password_hash=hashed_password)
    CRUD.mark_password_reset_token_as_used(db, token=token_data)

    return {"message": "Password has been reset successfully."}
