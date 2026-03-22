from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.plans import plan_service

router = APIRouter(prefix="/api/plans", tags=["plans"])


@router.get("")
def list_plan_catalog():
    """List all plan entitlements (config-driven)."""
    return plan_service.get_plans()


@router.get("/me")
def my_plan(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tier = plan_service.get_or_create_user_tier(db, current_user.id)
    return {
        "tier": tier,
        "entitlements": plan_service.get_plan(tier)
    }


@router.put("/me/{tier}")
def switch_my_plan(
    tier: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Placeholder self-service switch endpoint.
    # In production this should be controlled by payment webhook/admin flow.
    try:
        final_tier = plan_service.set_user_tier(db, current_user.id, tier)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid tier: {tier}")
    return {
        "tier": final_tier,
        "entitlements": plan_service.get_plan(final_tier)
    }
