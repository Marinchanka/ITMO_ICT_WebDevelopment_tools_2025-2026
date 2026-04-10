from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.database import get_session
from app.models import Review, User
from app.schemas import ReviewCreate, ReviewResponse
from app.auth import get_current_user

router = APIRouter(prefix="/reviews", tags=["reviews"])


# Оставить отзыв о пользователе
@router.post("/", response_model=ReviewResponse)
def create_review(
        review_data: ReviewCreate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    # Нельзя оставить отзыв самому себе
    if review_data.reviewed_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot review yourself")

    # Проверяем, что пользователь, о котором пишут отзыв, существует
    reviewed_user = session.get(User, review_data.reviewed_id)
    if not reviewed_user:
        raise HTTPException(status_code=404, detail="User to review not found")

    # Проверяем, не оставлял ли уже отзыв этот пользователь этому
    existing_review = session.exec(
        select(Review).where(
            Review.reviewer_id == current_user.id,
            Review.reviewed_id == review_data.reviewed_id
        )
    ).first()
    if existing_review:
        raise HTTPException(status_code=400, detail="You have already reviewed this user")

    # Создаём отзыв
    db_review = Review(
        rating=review_data.rating,
        comment=review_data.comment,
        reviewer_id=current_user.id,
        reviewed_id=review_data.reviewed_id
    )
    session.add(db_review)
    session.commit()
    session.refresh(db_review)
    return db_review


# Получить все отзывы о пользователе
@router.get("/user/{user_id}", response_model=List[ReviewResponse])
def get_user_reviews(
        user_id: int,
        session: Session = Depends(get_session)
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reviews = session.exec(
        select(Review).where(Review.reviewed_id == user_id)
    ).all()
    return reviews


# Получить все отзывы, написанные текущим пользователем
@router.get("/my", response_model=List[ReviewResponse])
def get_my_reviews(
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    reviews = session.exec(
        select(Review).where(Review.reviewer_id == current_user.id)
    ).all()
    return reviews


# Получить конкретный отзыв по ID
@router.get("/{review_id}", response_model=ReviewResponse)
def get_review(
        review_id: int,
        session: Session = Depends(get_session)
):
    review = session.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


# Удалить свой отзыв
@router.delete("/{review_id}")
def delete_review(
        review_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    review = session.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review.reviewer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your review")

    session.delete(review)
    session.commit()
    return {"message": "Review deleted"}