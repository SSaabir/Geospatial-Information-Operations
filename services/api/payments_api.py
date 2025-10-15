from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Numeric, ForeignKey, func
from typing import Optional
from datetime import datetime, timedelta, timezone
import os
from uuid import uuid4
import threading
import time
import logging

from db_config import DatabaseConfig
from models.user import Base, UserDB
from security.auth_middleware import get_current_user
from middleware.event_logger import log_auth_event, increment_usage_metrics
from utils.notification_manager import notify

logger = logging.getLogger(__name__)

db_config = DatabaseConfig()


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    plan = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    recurring = Column(Boolean, default=False)


class CheckoutSession(Base):
    __tablename__ = "checkout_sessions"
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    plan = Column(String(50), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    recurring = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    paid = Column(Boolean, default=False)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    last4 = Column(String(4), nullable=True)


class CreatePaymentRequest(BaseModel):
    plan: str = Field(..., description="Plan id: free|researcher|professional")
    amount: float = Field(..., description="Amount charged (USD)")
    recurring: Optional[bool] = Field(False, description="Whether the payment is recurring")


class CreateSessionRequest(BaseModel):
    plan: str = Field(...)
    recurring: Optional[bool] = Field(False)


class PayRequest(BaseModel):
    card_number: str = Field(..., description="Card number, digits only")
    exp_month: Optional[int] = Field(None, description="2-digit month")
    exp_year: Optional[int] = Field(None, description="2-digit or 4-digit year")
    cvc: Optional[str] = Field(None, description="CVC/CVV code")


class SessionResponse(BaseModel):
    session_id: str
    checkout_url: str


class PaymentResponse(BaseModel):
    id: int
    user_id: int
    amount: float
    plan: str
    created_at: datetime
    expires_at: datetime
    recurring: bool


payments_router = APIRouter(prefix="/payments", tags=["Payments"])


def get_db():
    db = db_config.get_session()
    try:
        yield db
    finally:
        db.close()


@payments_router.post("/create", response_model=PaymentResponse)
async def create_payment(
    body: CreatePaymentRequest,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Record a successful payment and set user's tier accordingly.

    This endpoint simulates payment acceptance. In production this would be
    triggered by a payment provider webhook after successful capture.
    """
    # Validate plan
    plan = (body.plan or "").strip().lower()
    allowed = {"free", "researcher", "professional"}
    if plan not in allowed:
        raise HTTPException(status_code=400, detail="Invalid plan")

    now = datetime.now(timezone.utc)
    expires = now + timedelta(days=30)

    payment = Payment(
        user_id=current_user.id,
        amount=round(body.amount, 2),
        plan=plan,
        created_at=now,
        expires_at=expires,
        recurring=bool(body.recurring),
    )

    db.add(payment)
    # Update user tier
    user = db.query(UserDB).filter(UserDB.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.tier = plan
    db.commit()
    db.refresh(payment)
    db.refresh(user)

    logger.info("Recorded payment %s for user %s plan %s recurring=%s", payment.id, user.username, plan, payment.recurring)
    try:
        log_auth_event("payment_recorded", user.id, True)
        increment_usage_metrics(user.id, api_calls=1)
    except Exception as e:
        logger.exception("Non-fatal: failed to log payment recorded: %s", e)

    # Notify about recorded payment (non-blocking)
    try:
        notify(
            subject="Payment Received",
            message=f"Your payment of ${float(payment.amount):.2f} for the {plan.title()} plan has been processed successfully.",
            level="success",
            metadata={"user_id": user.id, "payment_id": payment.id, "amount": float(payment.amount), "plan": plan},
            user_id=user.id
        )
    except Exception:
        logger.exception("Non-fatal: failed to send payment notification")

    return PaymentResponse(
        id=payment.id,
        user_id=payment.user_id,
        amount=float(payment.amount),
        plan=payment.plan,
        created_at=payment.created_at,
        expires_at=payment.expires_at,
        recurring=payment.recurring,
    )


@payments_router.post("/create-session", response_model=SessionResponse)
async def create_session(
    body: CreateSessionRequest,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    plan = (body.plan or "").strip().lower()
    allowed = {"free", "researcher", "professional"}
    if plan not in allowed:
        raise HTTPException(status_code=400, detail="Invalid plan")

    # simple pricing map
    prices = {"free": 0.0, "researcher": 29.0, "professional": 99.0}
    amount = float(prices.get(plan, 0.0))

    session_id = str(uuid4())
    session = CheckoutSession(
        id=session_id,
        user_id=current_user.id,
        plan=plan,
        amount=amount,
        recurring=bool(body.recurring),
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    checkout_url = f"/payments/session/{session_id}"  # frontend can open this or POST to pay
    try:
        log_auth_event("checkout_session_created", current_user.id, True)
        increment_usage_metrics(current_user.id, api_calls=1)
    except Exception as e:
        logger.exception("Non-fatal: failed to log checkout session creation: %s", e)
    # Notify user about checkout session creation
    try:
        notify(
            subject="Checkout Session Created",
            message=f"Your checkout session for the {plan.title()} plan (${amount:.2f}) is ready. Complete your payment to activate your subscription.",
            level="info",
            metadata={"user_id": current_user.id, "session_id": session_id, "amount": amount, "plan": plan},
            user_id=current_user.id
        )
    except Exception:
        logger.exception("Non-fatal: failed to send checkout-session notification")
    return SessionResponse(session_id=session_id, checkout_url=checkout_url)


def luhn_check(card_number: str) -> bool:
    # robust Luhn algorithm check for basic validation
    # Accept only digit characters; ensure plausible length (12-19)
    digits = [int(ch) for ch in card_number if ch.isdigit()]
    if len(digits) < 12 or len(digits) > 19:
        return False

    checksum = 0
    parity = len(digits) % 2
    for i, d in enumerate(digits):
        if i % 2 == parity:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0


@payments_router.post("/session/{session_id}/pay")
async def pay_session(session_id: str, payload: PayRequest, current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """Simulate paying a checkout session. Expects JSON payload matching PayRequest."""
    session = db.query(CheckoutSession).filter(CheckoutSession.id == session_id, CheckoutSession.user_id == current_user.id).first()
    if not session:
        logger.info("Payment attempt for missing session %s by user %s", session_id, getattr(current_user, 'username', 'unknown'))
        raise HTTPException(status_code=404, detail="Session not found")

    if session.paid:
        logger.info("Payment attempt for already-paid session %s by user %s", session_id, getattr(current_user, 'username', 'unknown'))
        raise HTTPException(status_code=400, detail="Session already paid")

    card_number = str(payload.card_number).strip()
    masked = f"**** **** **** {card_number[-4:]}" if len(card_number) >= 4 else "****"
    # Allow bypassing Luhn check in development for testing convenience
    skip_luhn = os.getenv('PAYMENT_SKIP_LUHN', 'false').lower() in ('1', 'true', 'yes')
    if not card_number or (not skip_luhn and not luhn_check(card_number)):
        if skip_luhn and card_number:
            logger.warning("PAYMENT_SKIP_LUHN is set: accepting card for session %s by user %s: %s", session_id, getattr(current_user, 'username', 'unknown'), masked)
        else:
            logger.info("Invalid card number provided for session %s by user %s: %s", session_id, getattr(current_user, 'username', 'unknown'), masked)
            raise HTTPException(status_code=400, detail="Invalid card number")

    last4 = card_number[-4:]
    now = datetime.now(timezone.utc)

    # create payment record
    payment = Payment(user_id=current_user.id, amount=session.amount, plan=session.plan, created_at=now, expires_at=now + timedelta(days=30), recurring=session.recurring)
    db.add(payment)

    # mark session paid
    session.paid = True
    session.paid_at = now
    session.last4 = last4
    
    # Set is_active to TRUE for paid subscriptions
    # First, deactivate any previous active sessions for this user
    from sqlalchemy import text
    db.execute(
        text("""
            UPDATE checkout_sessions 
            SET is_active = FALSE 
            WHERE user_id = :user_id 
            AND is_active = TRUE 
            AND id != :session_id
        """),
        {"user_id": current_user.id, "session_id": session_id}
    )
    
    # Add is_active column to session if it doesn't exist (for backwards compatibility)
    try:
        session.is_active = True
    except AttributeError:
        # Column doesn't exist yet - migration hasn't run
        pass

    # update user tier
    user = db.query(UserDB).filter(UserDB.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.tier = session.plan

    db.commit()
    db.refresh(payment)
    db.refresh(session)
    db.refresh(user)
    try:
        log_auth_event("payment_made", user.id, True)
        increment_usage_metrics(user.id, api_calls=1)
    except Exception as e:
        logger.exception("Non-fatal: failed to log payment made: %s", e)

    # Notify about successful payment (non-blocking)
    try:
        notify(
            subject="Payment Successful! 🎉",
            message=f"Congratulations! Your {session.plan.title()} plan is now active. You have full access to all premium features.",
            level="success",
            metadata={"user_id": user.id, "payment_id": payment.id, "amount": float(payment.amount), "plan": session.plan},
            user_id=user.id
        )
    except Exception:
        logger.exception("Non-fatal: failed to send payment-success notification")

    return {"success": True, "payment_id": payment.id, "user": {
        "username": user.username,
        "tier": user.tier,
    }}


@payments_router.get("/session/{session_id}")
async def get_session(session_id: str, current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(CheckoutSession).filter(CheckoutSession.id == session_id, CheckoutSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "session_id": session.id,
        "plan": session.plan,
        "amount": float(session.amount),
        "recurring": session.recurring,
        "paid": bool(session.paid),
        "last4": session.last4,
    }


@payments_router.get("/")
async def list_payments(current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """List payments for current user"""
    payments = db.query(Payment).filter(Payment.user_id == current_user.id).order_by(Payment.created_at.desc()).all()
    result = []
    for p in payments:
        result.append({
            "id": p.id,
            "user_id": p.user_id,
            "amount": float(p.amount),
            "plan": p.plan,
            "created_at": p.created_at,
            "expires_at": p.expires_at,
            "recurring": p.recurring,
        })
    return {"payments": result}


def expire_once(db: Session):
    now = datetime.now(timezone.utc)
    users = db.query(UserDB).filter(UserDB.tier != "free").all()
    for u in users:
        latest = db.query(Payment).filter(Payment.user_id == u.id).order_by(Payment.expires_at.desc()).first()
        if not latest:
            # No payment record -> revert to free
            u.tier = "free"
            db.commit()
            logger.info("Downgraded user %s due to missing payments", u.username)
            continue

        if latest.expires_at > now:
            continue

        # latest expired
        if latest.recurring:
            # auto-renew: create a new payment and extend
            new_expires = now + timedelta(days=30)
            p = Payment(user_id=u.id, amount=latest.amount, plan=latest.plan, created_at=now, expires_at=new_expires, recurring=True)
            db.add(p)
            u.tier = latest.plan
            db.commit()
            logger.info("Auto-renewed subscription for user %s", u.username)
        else:
            u.tier = "free"
            db.commit()
            logger.info("Downgraded user %s due to expired payment", u.username)
            try:
                notify(
                    subject="Subscription Expired",
                    message=f"Your subscription has expired and you've been moved to the Free plan. Upgrade anytime to regain access to premium features.",
                    level="warning",
                    metadata={"user_id": u.id},
                    user_id=u.id
                )
            except Exception:
                logger.exception("Non-fatal: failed to send subscription-downgrade notification")


def start_payment_expiry_worker(db_conf: DatabaseConfig, interval_seconds: Optional[int] = None):
    """Start a background thread that periodically expires/renews payments.

    interval_seconds can be set via environment variable PAYMENT_EXPIRY_INTERVAL_SECONDS
    (default 86400 seconds = 24 hours).
    """
    try:
        import os
        interval = int(os.getenv("PAYMENT_EXPIRY_INTERVAL_SECONDS", "86400")) if interval_seconds is None else interval_seconds
    except Exception:
        interval = 86400

    def worker():
        logger.info("Payment expiry worker started (interval=%s seconds)", interval)
        while True:
            db = db_conf.get_session()
            try:
                expire_once(db)
            except Exception as e:
                logger.exception("Payment expiry run failed: %s", e)
            finally:
                db.close()
            time.sleep(interval)

    t = threading.Thread(target=worker, daemon=True, name="payment-expiry-worker")
    t.start()
    return t
