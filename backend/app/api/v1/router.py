from fastapi import APIRouter

from app.api.v1 import accounts, assets, dashboard, households, integrations, liabilities, members, sync

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(households.router)
api_router.include_router(members.router)
api_router.include_router(accounts.router)
api_router.include_router(assets.router)
api_router.include_router(liabilities.router)
api_router.include_router(dashboard.router)
api_router.include_router(sync.router)
api_router.include_router(integrations.router)
