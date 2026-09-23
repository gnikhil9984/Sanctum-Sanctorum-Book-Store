"""Order operations: placing, paying and cancelling purchases."""
from datetime import datetime
from typing import Dict

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Book, Member, MemberTier, Order, OrderItem, OrderStatus
from app.schemas import OrderCreate
from app.services.members import ensure_can_access_restricted, get_member

TIER_DISCOUNT_PERCENT: Dict[str, int] = {
    MemberTier.APPRENTICE.value: 0,
    MemberTier.ADEPT.value: 5,
    MemberTier.MASTER.value: 10,
    MemberTier.SUPREME.value: 15,
}
BULK_QUANTITY_THRESHOLD = 10
BULK_DISCOUNT_PERCENT = 5


def calculate_discount_percent(member: Member, total_quantity: int) -> int:
    return TIER_DISCOUNT_PERCENT[member.tier] + (
        BULK_DISCOUNT_PERCENT if total_quantity >= BULK_QUANTITY_THRESHOLD else 0
    )


def create_order(db: Session, data: OrderCreate, now: datetime) -> Order:
    member = get_member(db, data.member_id)

    book_ids = [item.book_id for item in data.items]
    books_by_id = {book.id: book for book in db.scalars(select(Book).where(Book.id.in_(book_ids))).all()}
    missing = next((book_id for book_id in book_ids if book_id not in books_by_id), None)
    if missing is not None:
        raise HTTPException(status_code=404, detail="Book not found")

    books = [books_by_id[item.book_id] for item in data.items]
    if any(book.restricted for book in books):
        ensure_can_access_restricted(member)

    # Validate every requested quantity before mutating any stock. This makes the operation atomic
    # at the application level even when one item is scarce.
    for item, book in zip(data.items, books):
        if book.stock < item.quantity:
            raise HTTPException(status_code=409, detail=f"Insufficient stock for book {book.id}")

    order = Order(
        member_id=member.id,
        status=OrderStatus.PENDING.value,
        subtotal_cents=0,
        discount_percent=0,
        discount_cents=0,
        total_cents=0,
        created_at=now,
    )
    subtotal = 0
    total_quantity = 0

    for item, book in zip(data.items, books):
        book.stock -= item.quantity
        line_total = book.price_cents * item.quantity
        subtotal += line_total
        total_quantity += item.quantity
        order.items.append(
            OrderItem(
                book_id=book.id,
                quantity=item.quantity,
                unit_price_cents=book.price_cents,
            )
        )

    discount_percent = calculate_discount_percent(member, total_quantity)
    discount_cents = subtotal * discount_percent // 100
    order.subtotal_cents = subtotal
    order.discount_percent = discount_percent
    order.discount_cents = discount_cents
    order.total_cents = subtotal - discount_cents

    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def get_order(db: Session, order_id: int) -> Order:
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


def pay_order(db: Session, order_id: int) -> Order:
    order = get_order(db, order_id)
    if order.status != OrderStatus.PENDING.value:
        raise HTTPException(status_code=409, detail=f"Cannot pay an order that is {order.status}")
    order.status = OrderStatus.PAID.value
    db.commit()
    db.refresh(order)
    return order


def cancel_order(db: Session, order_id: int) -> Order:
    order = get_order(db, order_id)
    if order.status != OrderStatus.PENDING.value:
        raise HTTPException(status_code=409, detail=f"Cannot cancel an order that is {order.status}")

    for item in order.items:
        item.book.stock += item.quantity
    order.status = OrderStatus.CANCELLED.value
    db.commit()
    db.refresh(order)
    return order
