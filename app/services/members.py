"""Member operations and tier helpers."""
from datetime import datetime
from typing import List

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Loan, Member, MemberTier, Order, OrderStatus
from app.schemas import MemberCreate, MemberStats

TIER_ORDER: List[str] = [
    MemberTier.APPRENTICE.value,
    MemberTier.ADEPT.value,
    MemberTier.MASTER.value,
    MemberTier.SUPREME.value,
]
RESTRICTED_MIN_TIER = MemberTier.MASTER.value


def tier_at_least(tier: str, minimum: str) -> bool:
    return TIER_ORDER.index(tier) >= TIER_ORDER.index(minimum)


def ensure_can_access_restricted(member: Member) -> None:
    if not tier_at_least(member.tier, RESTRICTED_MIN_TIER):
        raise HTTPException(
            status_code=403, detail=f"Restricted books require tier '{RESTRICTED_MIN_TIER}' or higher"
        )


def create_member(db: Session, data: MemberCreate, now: datetime) -> Member:
    existing = db.scalar(select(Member).where(func.lower(Member.email) == data.email.lower()))
    if existing is not None:
        raise HTTPException(status_code=409, detail="A member with this email already exists")
    member = Member(name=data.name, email=data.email, tier=data.tier.value, created_at=now)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def get_member(db: Session, member_id: int) -> Member:
    member = db.get(Member, member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


def list_member_orders(db: Session, member_id: int) -> List[Order]:
    get_member(db, member_id)
    return list(db.scalars(select(Order).where(Order.member_id == member_id).order_by(Order.id)))


def get_member_stats(db: Session, member_id: int, now: datetime) -> MemberStats:
    get_member(db, member_id)

    paid_orders = db.scalars(
        select(Order).where(Order.member_id == member_id, Order.status == OrderStatus.PAID.value)
    ).all()
    loans = db.scalars(select(Loan).where(Loan.member_id == member_id)).all()

    active_loans = sum(loan.returned_at is None for loan in loans)
    overdue_loans = sum(
        loan.returned_at is None and now > loan.due_at for loan in loans
    )
    late_fees = sum(loan.late_fee_cents for loan in loans if loan.returned_at is not None)

    return MemberStats(
        member_id=member_id,
        orders_paid=len(paid_orders),
        total_spent_cents=sum(order.total_cents for order in paid_orders),
        active_loans=active_loans,
        overdue_loans=overdue_loans,
        late_fees_cents=late_fees,
    )
