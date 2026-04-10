# Лабораторная работа 1. Реализация серверного приложения FastAPI

**Цели:** Научиться реализовывать полноценное серверное приложение с помощью фреймворка FastAPI с применением дополнительных средств и библиотек.

**Тема:** Разработка веб-приложения для обмена книгами (буккросинг)

**Студент:** Машковцева Марина

**GitHub репозиторий:** `https://github.com/Marinchanka/ITMO_ICT_WebDevelopment_tools_2025-2026`

---

## Тема проекта

**Разработка веб-приложения для буккросинга**

Веб-приложение позволяет пользователям обмениваться книгами между собой. Функционал включает:

- **Создание профилей:** пользователи создают профили с информацией о себе
- **Добавление книг в библиотеку:** пользователи добавляют книги, которыми готовы поделиться
- **Поиск и запросы на обмен:** поиск книг других пользователей, отправка запросов на обмен
- **Управление запросами:** просмотр, подтверждение или отклонение запросов

**Технологии:**
- FastAPI — веб-фреймворк
- SQLModel — ORM (надстройка над SQLAlchemy)
- PostgreSQL — база данных
- Alembic — миграции
- JWT + bcrypt — аутентификация и хэширование

---

## Модели данных

Все модели реализованы с помощью **SQLModel** в файле `app/models.py`.

### Таблицы и связи

| № | Таблица | Поля | Связь |
|---|---------|------|-------|
| 1 | **User** | id, email, username, hashed_password, bio, city, created_at | |
| 2 | **Book** | id, title, author, genre, year, description, is_available, owner_id, created_at | owner_id → User.id |
| 3 | **ExchangeRequest** | id, message, status, requester_id, requested_book_id, offered_book_id, created_at | requester_id → User.id, requested_book_id → Book.id, offered_book_id → Book.id |
| 4 | **Review** | id, rating, comment, reviewer_id, reviewed_id, created_at | reviewer_id → User.id, reviewed_id → User.id |
| 5 | **Wishlist** | id, user_id, book_title, book_author, created_at | user_id → User.id |

### Связи между таблицами

- **User → Book** = один ко многим (один пользователь может иметь много книг)
- **User → ExchangeRequest** = один ко многим (один пользователь может отправлять много запросов)
- **User → Wishlist** = один ко многим (один пользователь может иметь много книг в вишлисте)
- **Book → ExchangeRequest** = один ко многим (одна книга может участвовать во многих запросах)
- **User ↔ User** = многие ко многим (через таблицу Review)

### Ассоциативная сущность

**ExchangeRequest** — связывает User и Book, имеет дополнительное поле `message` (сообщение к запросу), что соответствует требованию.

---

## Подключение к БД

**Файл:** `app/database.py`

```python
import os
from sqlmodel import SQLModel, Session, create_engine
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL")
engine = create_engine(db_url, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
```

**Файл:** `.env`
```env
DATABASE_URL=postgresql://postgres:200516@localhost:5432/bookcrossing_db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---
## Эндпоинты API

### Пользователи (users)

| Метод | Эндпоинт | Описание | Авторизация |
|-------|----------|----------|-------------|
| POST | `/users/register` | Регистрация нового пользователя | ❌ |
| GET | `/users/` | Список всех пользователей | ❌ |
| GET | `/users/me` | Информация о текущем пользователе | ✅ JWT |
| GET | `/users/{user_id}` | Получить пользователя с его книгами | ❌ |
| PUT | `/users/{user_id}/password` | Смена пароля | ❌ |

### Книги (books)

| Метод | Эндпоинт | Описание | Авторизация |
|-------|----------|----------|-------------|
| GET | `/books/` | Список всех книг | ❌ |
| GET | `/books/available` | Только доступные для обмена книги | ❌ |
| GET | `/books/{book_id}` | Детали книги + информация о владельце | ❌ |
| POST | `/books/` | Добавить новую книгу в библиотеку | ✅ JWT |
| DELETE | `/books/{book_id}` | Удалить свою книгу | ✅ JWT |

### Запросы на обмен (exchange-requests)

| Метод | Эндпоинт | Описание | Авторизация |
|-------|----------|----------|-------------|
| POST | `/exchange-requests/` | Создать запрос на обмен | ✅ JWT |
| GET | `/exchange-requests/` | Список моих запросов (входящие и исходящие) | ✅ JWT |
| GET | `/exchange-requests/{id}` | Детали конкретного запроса | ✅ JWT |
| PUT | `/exchange-requests/{id}?status=` | Подтвердить (accepted) или отклонить (rejected) | ✅ JWT |

### Вишлист (wishlist)

| Метод | Эндпоинт | Описание | Авторизация |
|-------|----------|----------|-------------|
| POST | `/wishlist/` | Добавить книгу в список желаний | ✅ JWT |
| GET | `/wishlist/` | Получить список желаний текущего пользователя | ✅ JWT |
| DELETE | `/wishlist/{id}` | Удалить книгу из вишлиста | ✅ JWT |

### Отзывы (reviews)

| Метод | Эндпоинт | Описание | Авторизация |
|-------|----------|----------|-------------|
| POST | `/reviews/` | Оставить отзыв о пользователе | ✅ JWT |
| GET | `/reviews/user/{user_id}` | Получить все отзывы о пользователе | ❌ |

### Аутентификация (auth)

| Метод | Эндпоинт | Описание | Авторизация |
|-------|----------|----------|-------------|
| POST | `/token` | Получить JWT токен (логин) | ❌ |

### Корневой эндпоинт

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/` | Приветственное сообщение |

---

## Аутентификация и JWT

### Реализация требования "п.3 вручную"

> **Требование:** реализовать авторизацию и JWT вручную, без использования сторонних библиотек (хэширование и создание JWT не в счет).

**Выполнено:**

- **JWT:** библиотека `python-jose` используется **только** для кодирования/декодирования токенов. Логика создания токена, проверки срока действия, извлечения пользователя из токена — написана **вручную** в файлах `auth.py` и `utils/security.py`.

- **Хэширование:** библиотека `passlib[bcrypt]` используется **только** для алгоритма хэширования. Функции-обертки `verify_password` и `get_password_hash` написаны **вручную** с дополнительной обработкой (обрезание пароля до 72 байт из-за ограничения bcrypt).

- **Аутентификация:** реализована через `OAuth2PasswordBearer` и `Depends(get_current_user)` без использования готовых решений типа `fastapi-users`.

**Файлы с ручной реализацией:**
- `app/auth.py` — `get_current_user()`
- `app/utils/security.py` — `create_access_token()`, `verify_password()`, `get_password_hash()`


### Пример использования JWT

```bash
# 1. Получение токена
POST /token
Content-Type: application/x-www-form-urlencoded

username=marina&password=123456

# Ответ:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}

# 2. Использование токена для защищенного эндпоинта
GET /users/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

---
## Миграции (Alembic)
Миграции настроены с помощью библиотеки **Alembic**. Все изменения схемы БД контролируются через миграции.

### Основные команды
```bash
# Создать новую миграцию (автоматическая генерация)
alembic revision --autogenerate -m "описание_изменений"

# Применить все миграции
alembic upgrade head

# Откатить последнюю миграцию
alembic downgrade -1

# Просмотреть историю миграций
alembic history

# Просмотреть текущую версию БД
alembic current
```

### Файлы миграций
Все миграции хранятся в папке migrations/versions/. Каждый файл миграции содержит:

- upgrade() — функция применения изменений

- downgrade() — функция отката изменений

---
## Запуск проекта
### Команды для запуска
```bash
# Применение миграций
alembic upgrade head

# Запуск сервера
uvicorn app.main:app --reload
```
