from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.integrations import get_registry
from app.models import Account
from app.schemas import AccountCreate, AccountOut

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("", response_model=AccountOut, status_code=status.HTTP_201_CREATED)
def create_account(body: AccountCreate, db: Session = Depends(get_db)) -> Account:
    if get_registry().account(body.institution_code) is None:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown institution_code '{body.institution_code}'. "
            f"Available: {get_registry().list_accounts()}",
        )
    account = Account(**body.model_dump())
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


@router.get("", response_model=list[AccountOut])
def list_accounts(household_id: int, db: Session = Depends(get_db)) -> list[Account]:
    return list(
        db.scalars(select(Account).where(Account.household_id == household_id)).all()
    )
