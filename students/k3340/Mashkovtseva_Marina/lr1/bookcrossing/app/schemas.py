from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from enum import Enum


class RequestStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    bio: Optional[str] = ""
    city: Optional[str] = ""


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserWithBooks(UserResponse):
    books: List["BookResponse"] = []


# Book schemas
class BookBase(BaseModel):
    title: str
    author: str
    genre: str
    year: int
    description: Optional[str] = ""


class BookCreate(BookBase):
    pass


class BookResponse(BookBase):
    id: int
    owner_id: int
    is_available: bool
    created_at: datetime

    class Config:
        from_attributes = True


class BookWithOwner(BookResponse):
    owner: UserResponse


# Exchange Request schemas
class ExchangeRequestCreate(BaseModel):
    requested_book_id: int
    offered_book_id: int
    message: str


class ExchangeRequestResponse(BaseModel):
    id: int
    message: str
    status: RequestStatus
    created_at: datetime
    requester_id: int
    requested_book_id: int
    offered_book_id: int

    class Config:
        from_attributes = True


class ExchangeRequestWithDetails(ExchangeRequestResponse):
    requester: UserResponse
    requested_book: BookResponse
    offered_book: BookResponse


# Review schemas
class ReviewCreate(BaseModel):
    rating: int
    comment: Optional[str] = ""


class ReviewResponse(BaseModel):
    id: int
    rating: int
    comment: str
    created_at: datetime
    reviewer_id: int
    reviewed_id: int

    class Config:
        from_attributes = True


# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# Wishlist schemas
class WishlistCreate(BaseModel):
    book_title: str
    book_author: Optional[str] = ""


class WishlistResponse(WishlistCreate):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ExchangeRequest schemas (если ещё нет)
class ExchangeRequestCreate(BaseModel):
    requested_book_id: int
    offered_book_id: int
    message: str


class ExchangeRequestResponse(BaseModel):
    id: int
    message: str
    status: str
    created_at: datetime
    requester_id: int
    requested_book_id: int
    offered_book_id: int

    class Config:
        from_attributes = True


class ExchangeRequestWithDetails(ExchangeRequestResponse):
    requester: UserResponse
    requested_book: BookResponse
    offered_book: BookResponse

# Обновление ссылок
BookResponse.model_rebuild()
UserWithBooks.model_rebuild()