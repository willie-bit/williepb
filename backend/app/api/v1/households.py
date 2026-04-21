from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, get_auth_context
from app.db.session import get_db
from app.models import Household
from app.schemas import HouseholdOut

router = APIRouter(prefix="/households", tags=["households"])


@router.get("/mine", response_model=HouseholdOut)
def my_household(
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
) -> Household:
    return db.get(Household, ctx.household_id)
