from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, get_auth_context
from app.db.session import get_db
from app.models import Asset
from app.schemas import AssetCreate, AssetOut, AssetUpdate

router = APIRouter(prefix="/assets", tags=["assets"])


@router.post("", response_model=AssetOut, status_code=status.HTTP_201_CREATED)
def create_asset(
    body: AssetCreate,
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
) -> Asset:
    if body.household_id != ctx.household_id:
        raise HTTPException(status_code=403, detail="household mismatch")
    asset = Asset(**body.model_dump())
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


@router.get("", response_model=list[AssetOut])
def list_assets(
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
) -> list[Asset]:
    return list(
        db.scalars(select(Asset).where(Asset.household_id == ctx.household_id)).all()
    )


@router.patch("/{asset_id}", response_model=AssetOut)
def update_asset(
    asset_id: int,
    body: AssetUpdate,
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
) -> Asset:
    asset = db.get(Asset, asset_id)
    if asset is None or asset.household_id != ctx.household_id:
        raise HTTPException(status_code=404, detail="Asset not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(asset, k, v)
    db.commit()
    db.refresh(asset)
    return asset


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(
    asset_id: int,
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
) -> None:
    asset = db.get(Asset, asset_id)
    if asset is None or asset.household_id != ctx.household_id:
        raise HTTPException(status_code=404, detail="Asset not found")
    db.delete(asset)
    db.commit()
