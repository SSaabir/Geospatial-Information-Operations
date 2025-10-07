"""Billing API (Stripe removed).

This module intentionally avoids any third-party payment provider calls.
It provides simple, server-side tier-change endpoints for regions where
external processors are not available. In production you should add proper
authorization and audit logging before granting paid tiers.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from models.user import UserResponse
from sqlalchemy.orm import Session

from security.auth_middleware import get_current_user
from models.user import UserDB
from db_config import DatabaseConfig


billing_router = APIRouter(prefix="/billing", tags=["Billing"])

db_config = DatabaseConfig()


def get_db():
    db = db_config.get_session()
    try:
        yield db
    finally:
        db.close()


class ChangeTierRequest(BaseModel):
    tier: str


class CheckoutRequest(BaseModel):
    plan_id: str


logger = logging.getLogger(__name__)


@billing_router.get("/plans")
async def get_plans():
    """Return available plans and a brief description."""
    plans = [
        {"id": "free", "name": "Free", "price": "$0/mo"},
        {"id": "researcher", "name": "Researcher", "price": "$29/mo"},
        {"id": "professional", "name": "Professional", "price": "$99/mo"},
    ]
    return {"plans": plans}


@billing_router.post("/change-tier")
async def change_tier(
    body: ChangeTierRequest,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change the authenticated user's tier directly.

    No external payment provider is configured in this repository. In a
    production deployment you should add proper business rules, authorization
    and audit logging before granting paid tiers.
    """
    requested = (body.tier or "").strip().lower()
    allowed = {"free", "researcher", "professional"}
    if requested not in allowed:
        raise HTTPException(status_code=400, detail="Invalid tier")

    user = db.query(UserDB).filter(UserDB.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.tier = requested
    db.commit()
    db.refresh(user)
    logger.info("User %s tier changed to %s via change-tier API", user.username, requested)

    # Return a compact success response for API clients
    # and also return the updated user object for frontend compatibility
    return {"success": True, "tier": requested, "user": UserResponse.from_orm(user).dict()}


@billing_router.post("/create-checkout-session")
async def create_checkout_session(
    body: CheckoutRequest,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Compatibility endpoint: previously used for external checkout.

    Kept for compatibility with older clients. Now performs a direct tier
    change and returns a message. No external payments are processed.
    """
    plan_id = (body.plan_id or "").strip().lower()
    allowed = {"free", "researcher", "professional"}
    if plan_id not in allowed:
        raise HTTPException(status_code=400, detail="Invalid plan")

    user = db.query(UserDB).filter(UserDB.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.tier = plan_id
    db.commit()
    db.refresh(user)
    logger.info("User %s tier changed to %s via create-checkout-session (compat)", user.username, plan_id)

    return {"success": True, "message": f"Tier changed to {plan_id}", "url": None, "user": UserResponse.from_orm(user).dict()}


@billing_router.post("/webhook")
async def billing_webhook(request: Request):
    """No-op webhook endpoint kept for compatibility.

    External payment providers are not configured in this project. Webhook
    payloads are ignored and acknowledged to avoid 404s from external systems.
    """
    return {"received": True, "note": "No external webhook processing configured"}


