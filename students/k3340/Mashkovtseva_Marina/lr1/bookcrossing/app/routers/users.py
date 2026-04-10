from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.database import get_session
from app.models import User
from app.schemas import UserCreate, UserResponse, UserWithBooks
from app.utils.security import get_password_hash
from app.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Получить информацию о текущем авторизованном пользователе"""
    return current_user


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, session: Session = Depends(get_session)):
    existing_user = session.exec(select(User).where(
        (User.username == user.username) | (User.email == user.email)
    )).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        bio=user.bio,
        city=user.city
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.get("/", response_model=List[UserResponse])
def get_users(session: Session = Depends(get_session)):
    """Список всех пользователей"""
    return session.exec(select(User)).all()


@router.get("/{user_id}", response_model=UserWithBooks)
def get_user(user_id: int, session: Session = Depends(get_session)):
    """Получить пользователя по ID с его книгами"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}/password")
def change_password(user_id: int, new_password: str, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.hashed_password = get_password_hash(new_password)
    session.add(user)
    session.commit()
    return {"message": "Password updated"}