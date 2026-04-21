from fastapi import APIRouter
from pydantic import BaseModel

from app.integrations import get_registry

router = APIRouter(prefix="/integrations", tags=["integrations"])


class IntegrationsCatalog(BaseModel):
    accounts: list[str]
    markets: list[str]
    realestate: list[str]


@router.get("", response_model=IntegrationsCatalog)
def list_integrations() -> IntegrationsCatalog:
    reg = get_registry()
    return IntegrationsCatalog(
        accounts=reg.list_accounts(),
        markets=reg.list_markets(),
        realestate=reg.list_realestate(),
    )
