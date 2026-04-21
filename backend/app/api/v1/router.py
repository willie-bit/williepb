from fastapi import APIRouter

from app.api.v1 import (
    accounts,
    assets,
    auth,
    dashboard,
    households,
    integrations,
    liabilities,
    members,
    sync,
    tax,
    timeseries,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(households.router)
api_router.include_router(members.router)
api_router.include_router(accounts.router)
api_router.include_router(assets.router)
api_router.include_router(liabilities.router)
api_router.include_router(dashboard.router)
api_router.include_router(timeseries.router)
api_router.include_router(tax.router)
api_router.include_router(sync.router)
api_router.include_router(integrations.router)
