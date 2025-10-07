import os
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
import stripe

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


stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")


class CheckoutRequest(BaseModel):
    plan_id: str


def _price_for_plan(plan_id: str) -> str:
    if plan_id == "researcher":
        price = os.getenv("STRIPE_PRICE_RESEARCHER", "")
    elif plan_id == "professional":
        price = os.getenv("STRIPE_PRICE_PROFESSIONAL", "")
    else:
        price = ""
    return price


@billing_router.post("/create-checkout-session")
async def create_checkout_session(
    body: CheckoutRequest,
    current_user: UserDB = Depends(get_current_user)
):
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe is not configured")

    plan_id = body.plan_id
    if plan_id == "free":
        # direct downgrade without Stripe
        return {"url": None, "message": "Use /auth/me/tier to switch to free"}

    price_id = _price_for_plan(plan_id)
    if not price_id:
        raise HTTPException(status_code=400, detail="Invalid or unconfigured plan")

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")

    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=f"{frontend_url}/pricing?success=true",
            cancel_url=f"{frontend_url}/pricing?canceled=true",
            client_reference_id=f"{current_user.id}:{plan_id}",
            metadata={"user_id": str(current_user.id), "plan_id": plan_id},
        )
        return {"url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stripe error: {e}")


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


