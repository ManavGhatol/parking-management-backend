from fastapi import APIRouter, Depends, HTTPException, status
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Any

from ..database import get_db
from ..models import User
from ..schemas import UserCreate, UserResponse, Token
from ..auth import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)) -> Any:
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user_by_username = db.query(User).filter(User.username == user_in.username).first()
    if user_by_username:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists.",
        )
    
    user_obj = User(
        username=user_in.username,
        email=user_in.email,
        full_name=user_in.full_name,
        phone_number=user_in.phone_number,
        password_hash=get_password_hash(user_in.password),
        user_type=user_in.user_type
    )
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj

@router.post("/login", response_model=Token)
def login_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_type": user.user_type.value}, expires_delta=access_token_expires
    )
    
    # Update last login
    from datetime import datetime
    user.last_login = datetime.utcnow()
    db.commit()

    return {"access_token": access_token, "token_type": "bearer"}
