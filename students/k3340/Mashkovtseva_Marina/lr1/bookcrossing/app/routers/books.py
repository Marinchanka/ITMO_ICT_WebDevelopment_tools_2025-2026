from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models import Book, User
from app.schemas import BookCreate, BookResponse, BookWithOwner
from app.auth import get_current_user
from typing import List

router = APIRouter(prefix="/books", tags=["books"])

@router.get("/", response_model=List[BookResponse])
def get_books(session: Session = Depends(get_session)):
    return session.exec(select(Book)).all()

@router.get("/available", response_model=List[BookResponse])
def get_available_books(session: Session = Depends(get_session)):
    return session.exec(select(Book).where(Book.is_available == True)).all()

@router.get("/{book_id}", response_model=BookWithOwner)
def get_book(book_id: int, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.post("/", response_model=BookResponse)
def create_book(book: BookCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    db_book = Book(**book.dict(), owner_id=current_user.id)
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book

@router.delete("/{book_id}")
def delete_book(book_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your book")
    session.delete(book)
    session.commit()
    return {"message": "Book deleted"}