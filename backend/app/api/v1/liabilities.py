from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Liability
from app.schemas import LiabilityCreate, LiabilityOut

router = APIRouter(prefix="/liabilities", tags=["liabilities"])


@router.post("", response_model=LiabilityOut, status_code=status.HTTP_201_CREATED)
def create_liability(body: LiabilityCreate, db: Session = Depends(get_db)) -> Liability:
    liab = Liability(**body.model_dump())
    db.add(liab)
    db.commit()
    db.refresh(liab)
    return liab


@router.get("", response_model=list[LiabilityOut])
def list_liabilities(household_id: int, db: Session = Depends(get_db)) -> list[Liability]:
    return list(
        db.scalars(select(Liability).where(Liability.household_id == household_id)).all()
    )


@router.delete("/{liability_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_liability(liability_id: int, db: Session = Depends(get_db)) -> None:
    liab = db.get(Liability, liability_id)
    if liab is None:
        raise HTTPException(status_code=404, detail="Liability not found")
    db.delete(liab)
    db.commit()
