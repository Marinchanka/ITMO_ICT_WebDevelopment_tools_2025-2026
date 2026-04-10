from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum


# Перечисление статусов запроса
class RequestStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


# Ассоциативная сущность для запросов на обмен
class ExchangeRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    message: str
    status: str = Field(default="pending")
    created_at: datetime = Field(default_factory=datetime.now)

    requester_id: int = Field(foreign_key="user.id")
    requested_book_id: int = Field(foreign_key="book.id")
    offered_book_id: int = Field(foreign_key="book.id")

    requester: Optional["User"] = Relationship(
        back_populates="sent_requests",
        sa_relationship_kwargs={"foreign_keys": "ExchangeRequest.requester_id"}
    )
    requested_book: Optional["Book"] = Relationship(
        back_populates="incoming_requests",
        sa_relationship_kwargs={"foreign_keys": "ExchangeRequest.requested_book_id"}
    )
    offered_book: Optional["Book"] = Relationship(
        back_populates="outgoing_requests",
        sa_relationship_kwargs={"foreign_keys": "ExchangeRequest.offered_book_id"}
    )

# Модель пользователя
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    bio: Optional[str] = ""
    city: Optional[str] = ""
    created_at: datetime = Field(default_factory=datetime.now)

    # Связи
    books: List["Book"] = Relationship(back_populates="owner")
    sent_requests: List["ExchangeRequest"] = Relationship(
        back_populates="requester",
        sa_relationship_kwargs={"foreign_keys": "ExchangeRequest.requester_id"}
    )
    reviews_written: List["Review"] = Relationship(
        back_populates="reviewer",
        sa_relationship_kwargs={"foreign_keys": "Review.reviewer_id"}
    )
    reviews_received: List["Review"] = Relationship(
        back_populates="reviewed",
        sa_relationship_kwargs={"foreign_keys": "Review.reviewed_id"}
    )
    wishlist_items: List["Wishlist"] = Relationship(back_populates="user")

# Модель книги
class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    author: str
    genre: str
    year: int
    description: Optional[str] = ""
    is_available: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    owner_id: int = Field(foreign_key="user.id")

    owner: Optional["User"] = Relationship(back_populates="books")
    incoming_requests: List["ExchangeRequest"] = Relationship(
        back_populates="requested_book",
        sa_relationship_kwargs={"foreign_keys": "ExchangeRequest.requested_book_id"}
    )
    outgoing_requests: List["ExchangeRequest"] = Relationship(
        back_populates="offered_book",
        sa_relationship_kwargs={"foreign_keys": "ExchangeRequest.offered_book_id"}
    )


# Модель отзыва (many-to-many с доп. полями)
class Review(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    rating: int
    comment: Optional[str] = ""
    created_at: datetime = Field(default_factory=datetime.now)

    # Внешние ключи
    reviewer_id: int = Field(foreign_key="user.id")
    reviewed_id: int = Field(foreign_key="user.id")

    # Связи — указываем foreign_keys явно
    reviewer: Optional["User"] = Relationship(
        back_populates="reviews_written",
        sa_relationship_kwargs={"foreign_keys": "Review.reviewer_id"}
    )
    reviewed: Optional["User"] = Relationship(
        back_populates="reviews_received",
        sa_relationship_kwargs={"foreign_keys": "Review.reviewed_id"}
    )

class Wishlist(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    book_title: str
    book_author: Optional[str] = ""
    created_at: datetime = Field(default_factory=datetime.now)

    # Связь с пользователем
    user: "User" = Relationship(back_populates="wishlist_items")