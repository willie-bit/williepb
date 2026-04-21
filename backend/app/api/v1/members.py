from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Household, Member
from app.schemas import MemberCreate, MemberOut

router = APIRouter(prefix="/members", tags=["members"])


@router.post("", response_model=MemberOut, status_code=status.HTTP_201_CREATED)
def create_member(body: MemberCreate, db: Session = Depends(get_db)) -> Member:
    if db.get(Household, body.household_id) is None:
        raise HTTPException(status_code=404, detail="Household not found")
    member = Member(
        household_id=body.household_id,
        name=body.name,
        email=body.email,
        role=body.role,
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.get("", response_model=list[MemberOut])
def list_members(household_id: int, db: Session = Depends(get_db)) -> list[Member]:
    return list(
        db.scalars(select(Member).where(Member.household_id == household_id)).all()
    )
