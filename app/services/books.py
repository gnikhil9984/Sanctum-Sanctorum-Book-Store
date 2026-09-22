"""Book catalogue operations."""
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import Book
from app.schemas import BookCreate, BookPage, BookSort, BookUpdate


def create_book(db: Session, data: BookCreate) -> Book:
    existing = db.scalar(select(Book).where(Book.isbn == data.isbn))
    if existing is not None:
        raise HTTPException(status_code=409, detail="A book with this ISBN already exists")

    book = Book(**data.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def get_book(db: Session, book_id: int) -> Book:
    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


def update_book(db: Session, book_id: int, data: BookUpdate) -> Book:
    book = get_book(db, book_id)
    for field in ("title", "author", "price_cents", "stock", "restricted"):
        if field in data.model_fields_set:
            setattr(book, field, getattr(data, field))
    db.commit()
    db.refresh(book)
    return book


def list_books(
    db: Session,
    q: Optional[str] = None,
    restricted: Optional[bool] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    sort: Optional[BookSort] = None,
    limit: int = 20,
    offset: int = 0,
) -> BookPage:
    query = select(Book)
    count_query = select(func.count()).select_from(Book)

    filters = []
    if q:
        pattern = f"%{q}%"
        filters.append(or_(Book.title.ilike(pattern), Book.author.ilike(pattern)))
    if restricted is not None:
        filters.append(Book.restricted == restricted)
    if min_price is not None:
        filters.append(Book.price_cents >= min_price)
    if max_price is not None:
        filters.append(Book.price_cents <= max_price)

    if filters:
        query = query.where(*filters)
        count_query = count_query.where(*filters)

    if sort == "title":
        query = query.order_by(Book.title.asc(), Book.id.asc())
    elif sort == "-title":
        query = query.order_by(Book.title.desc(), Book.id.asc())
    elif sort == "price":
        query = query.order_by(Book.price_cents.asc(), Book.id.asc())
    elif sort == "-price":
        query = query.order_by(Book.price_cents.desc(), Book.id.asc())
    else:
        query = query.order_by(Book.id.asc())

    books = db.scalars(query.limit(limit).offset(offset)).all()
    total = db.scalar(count_query) or 0
    return BookPage(items=books, total=total, limit=limit, offset=offset)
