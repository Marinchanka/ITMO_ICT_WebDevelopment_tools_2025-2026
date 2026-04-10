from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.database import get_session
from app.models import Wishlist, User
from app.schemas import WishlistCreate, WishlistResponse
from app.auth import get_current_user

router = APIRouter(prefix="/wishlist", tags=["wishlist"])

# Добавить книгу в вишлист
@router.post("/", response_model=WishlistResponse)
def add_to_wishlist(
    item: WishlistCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    db_item = Wishlist(
        user_id=current_user.id,
        book_title=item.book_title,
        book_author=item.book_author
    )
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

# Получить вишлист текущего пользователя
@router.get("/", response_model=List[WishlistResponse])
def get_my_wishlist(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    items = session.exec(select(Wishlist).where(Wishlist.user_id == current_user.id)).all()
    return items

# Удалить из вишлиста
@router.delete("/{item_id}")
def delete_wishlist_item(
    item_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    item = session.get(Wishlist, item_id)
    if not item or item.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Item not found")
    session.delete(item)
    session.commit()
    return {"message": "Item removed from wishlist"}