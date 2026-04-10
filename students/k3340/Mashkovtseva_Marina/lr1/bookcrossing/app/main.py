from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from datetime import timedelta
from app.database import init_db, get_session
from app.models import User
from app.schemas import Token
from app.utils.security import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.routers import users, books, exchange_requests, wishlist
from app.auth import get_current_user

app = FastAPI(title="BookCrossing API", version="1.0.0")

# Подключение роутеров
app.include_router(users.router)
app.include_router(books.router)
app.include_router(exchange_requests.router)
app.include_router(wishlist.router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/")
def root():
    return {"message": "Welcome to BookCrossing API!"}