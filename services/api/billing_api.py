import os
import logging
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
import stripe

from security.auth_middleware import get_current_user
from models.user import UserDB
from db_config import DatabaseConfig
from middleware.event_logger import log_auth_event, increment_usage_metrics


billing_router = APIRouter(prefix="/billing", tags=["Billing"])

db_config = DatabaseConfig()


def get_db():
    db = db_config.get_session()
    try:
        yield db
    finally:
        db.close()


stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")


class CheckoutRequest(BaseModel):
    plan_id: str


class ChangeTierRequest(BaseModel):
    tier: str


class UserResponse(BaseModel):
    id: int
    username: str
    tier: str
    
    class Config:
        orm_mode = True


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
    try:
        log_auth_event("tier_changed", user.id, True, failure_reason=None)
        increment_usage_metrics(user.id, api_calls=1)
    except Exception as e:
        logger.exception("Non-fatal: failed to log tier change: %s", e)

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
    try:
        log_auth_event("tier_changed_compat", user.id, True)
        increment_usage_metrics(user.id, api_calls=1)
    except Exception as e:
        logger.exception("Non-fatal: failed to log tier change (compat): %s", e)

    return {"success": True, "message": f"Tier changed to {plan_id}", "url": None, "user": UserResponse.from_orm(user).dict()}


@billing_router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")

    try:
        if endpoint_secret:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        else:
            # No verification (dev only)
            event = stripe.Event.construct_from(request.json(), stripe.api_key)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        ref = session.get("client_reference_id", "")
        try:
            user_id_str, plan_id = ref.split(":", 1)
            user_id = int(user_id_str)
        except Exception:
            user_id, plan_id = None, None

        if user_id and plan_id in {"researcher", "professional"}:
            user = db.query(UserDB).filter(UserDB.id == user_id).first()
            if user:
                user.tier = plan_id
                db.commit()

    return {"received": True}


