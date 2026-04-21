from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, get_auth_context
from app.db.session import get_db
from app.models import Liability
from app.schemas import LiabilityCreate, LiabilityOut

router = APIRouter(prefix="/liabilities", tags=["liabilities"])


@router.post("", response_model=LiabilityOut, status_code=status.HTTP_201_CREATED)
def create_liability(
    body: LiabilityCreate,
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
) -> Liability:
    if body.household_id != ctx.household_id:
        raise HTTPException(status_code=403, detail="household mismatch")
    liab = Liability(**body.model_dump())
    db.add(liab)
    db.commit()
    db.refresh(liab)
    return liab


@router.get("", response_model=list[LiabilityOut])
def list_liabilities(
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
) -> list[Liability]:
    return list(
        db.scalars(select(Liability).where(Liability.household_id == ctx.household_id)).all()
    )


@router.delete("/{liability_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_liability(
    liability_id: int,
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
) -> None:
    liab = db.get(Liability, liability_id)
    if liab is None or liab.household_id != ctx.household_id:
        raise HTTPException(status_code=404, detail="Liability not found")
    db.delete(liab)
    db.commit()
