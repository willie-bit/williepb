from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Household
from app.schemas import HouseholdCreate, HouseholdOut

router = APIRouter(prefix="/households", tags=["households"])


@router.post("", response_model=HouseholdOut, status_code=status.HTTP_201_CREATED)
def create_household(body: HouseholdCreate, db: Session = Depends(get_db)) -> Household:
    hh = Household(name=body.name, base_currency=body.base_currency)
    db.add(hh)
    db.commit()
    db.refresh(hh)
    return hh


@router.get("", response_model=list[HouseholdOut])
def list_households(db: Session = Depends(get_db)) -> list[Household]:
    return list(db.scalars(select(Household)).all())


@router.get("/{household_id}", response_model=HouseholdOut)
def get_household(household_id: int, db: Session = Depends(get_db)) -> Household:
    hh = db.get(Household, household_id)
    if hh is None:
        raise HTTPException(status_code=404, detail="Household not found")
    return hh
