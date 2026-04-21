from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, get_auth_context
from app.db.session import get_db
from app.integrations import get_registry
from app.models import Account
from app.schemas import AccountCreate, AccountOut

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("", response_model=AccountOut, status_code=status.HTTP_201_CREATED)
def create_account(
    body: AccountCreate,
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
) -> Account:
    if body.household_id != ctx.household_id:
        raise HTTPException(status_code=403, detail="household mismatch")
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
def list_accounts(
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
) -> list[Account]:
    return list(
        db.scalars(select(Account).where(Account.household_id == ctx.household_id)).all()
    )
