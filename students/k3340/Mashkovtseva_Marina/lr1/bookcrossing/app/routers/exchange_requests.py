from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.database import get_session
from app.models import ExchangeRequest, Book, User
from app.schemas import ExchangeRequestCreate, ExchangeRequestResponse, ExchangeRequestWithDetails
from app.auth import get_current_user

router = APIRouter(prefix="/exchange-requests", tags=["exchange-requests"])


# Создать запрос на обмен
@router.post("/", response_model=ExchangeRequestResponse)
def create_exchange_request(
        request_data: ExchangeRequestCreate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    # Проверяем, что запрашиваемая книга существует и доступна
    requested_book = session.get(Book, request_data.requested_book_id)
    if not requested_book:
        raise HTTPException(status_code=404, detail="Requested book not found")
    if not requested_book.is_available:
        raise HTTPException(status_code=400, detail="Requested book is not available")

    # Нельзя запрашивать свою книгу
    if requested_book.owner_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot request your own book")

    # Проверяем, что предлагаемая книга существует и принадлежит текущему пользователю
    offered_book = session.get(Book, request_data.offered_book_id)
    if not offered_book:
        raise HTTPException(status_code=404, detail="Offered book not found")
    if offered_book.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only offer your own books")

    # Проверяем, нет ли уже активного запроса на эти книги
    existing_request = session.exec(
        select(ExchangeRequest).where(
            ExchangeRequest.requested_book_id == request_data.requested_book_id,
            ExchangeRequest.requester_id == current_user.id,
            ExchangeRequest.status == "pending"
        )
    ).first()
    if existing_request:
        raise HTTPException(status_code=400, detail="You already have a pending request for this book")

    # Создаём запрос
    db_request = ExchangeRequest(
        message=request_data.message,
        requester_id=current_user.id,
        requested_book_id=request_data.requested_book_id,
        offered_book_id=request_data.offered_book_id,
        status="pending"
    )
    session.add(db_request)
    session.commit()
    session.refresh(db_request)
    return db_request


# Получить все запросы (для текущего пользователя: отправленные и полученные)
@router.get("/", response_model=List[ExchangeRequestWithDetails])
def get_my_exchanges(
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    # Запросы, где пользователь отправитель
    sent = session.exec(
        select(ExchangeRequest).where(ExchangeRequest.requester_id == current_user.id)
    ).all()

    # Запросы, где пользователь получатель (кто-то хочет его книгу)
    received = session.exec(
        select(ExchangeRequest).where(ExchangeRequest.requested_book.has(owner_id=current_user.id))
    ).all()

    # Объединяем и убираем дубликаты
    all_requests = {r.id: r for r in sent + received}.values()
    return list(all_requests)


# Обновить статус запроса (подтвердить/отклонить)
@router.put("/{request_id}")
def update_request_status(
        request_id: int,
        status: str,  # "accepted" or "rejected"
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    if status not in ["accepted", "rejected"]:
        raise HTTPException(status_code=400, detail="Status must be 'accepted' or 'rejected'")

    db_request = session.get(ExchangeRequest, request_id)
    if not db_request:
        raise HTTPException(status_code=404, detail="Request not found")

    # Проверяем, что текущий пользователь является владельцем запрашиваемой книги (получатель запроса)
    requested_book = session.get(Book, db_request.requested_book_id)
    if requested_book.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not the owner of the requested book")

    # Проверяем, что запрос ещё не обработан
    if db_request.status != "pending":
        raise HTTPException(status_code=400, detail=f"Request already {db_request.status}")

    offered_book = session.get(Book, db_request.offered_book_id)

    if status == "accepted":
        # Меняем владельцев книг
        original_owner_id = requested_book.owner_id

        # Книга, которую запрашивали, переходит к отправителю запроса
        requested_book.owner_id = db_request.requester_id
        requested_book.is_available = False

        # Книга, которую предлагали, переходит к бывшему владельцу запрашиваемой книги
        offered_book.owner_id = original_owner_id
        offered_book.is_available = False

        session.add(requested_book)
        session.add(offered_book)
        db_request.status = "accepted"

    else:  # rejected
        db_request.status = "rejected"
        # Книги остаются доступными
        requested_book.is_available = True
        offered_book.is_available = True
        session.add(requested_book)
        session.add(offered_book)

    session.add(db_request)
    session.commit()

    return {
        "message": f"Request {status}",
        "exchange": {
            "requested_book_id": db_request.requested_book_id,
            "offered_book_id": db_request.offered_book_id,
            "new_owner_of_requested": requested_book.owner_id,
            "new_owner_of_offered": offered_book.owner_id
        }
    }


# Получить конкретный запрос по ID
@router.get("/{request_id}", response_model=ExchangeRequestWithDetails)
def get_exchange_request(
        request_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    db_request = session.get(ExchangeRequest, request_id)
    if not db_request:
        raise HTTPException(status_code=404, detail="Request not found")

    # Проверяем, что пользователь участвует в этом запросе
    requested_book = session.get(Book, db_request.requested_book_id)
    if db_request.requester_id != current_user.id and requested_book.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not involved in this exchange")

    return db_request