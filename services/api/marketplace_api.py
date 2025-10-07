from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from security.auth_middleware import get_current_user
from models.user import UserDB
from models.usage import UsageMetrics
from db_config import DatabaseConfig

marketplace_router = APIRouter(prefix="/marketplace", tags=["Marketplace"])
db_config = DatabaseConfig()

def get_db():
    db = db_config.get_session()
    try:
        yield db
    finally:
        db.close()

# In-memory catalog placeholder
catalog = [
    {"id": 1, "name": "Dataset #1", "region": "Global", "size_mb": 120},
    {"id": 2, "name": "Dataset #2", "region": "Europe", "size_mb": 85},
    {"id": 3, "name": "Dataset #3", "region": "Asia", "size_mb": 200},
    {"id": 4, "name": "Dataset #4", "region": "Americas", "size_mb": 150},
]


@marketplace_router.get("/catalog", response_model=List[Dict[str, Any]])
async def list_catalog():
    return catalog


@marketplace_router.post("/download/{dataset_id}")
async def download_dataset(dataset_id: int, current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    # Gate downloads to researcher and above
    if (getattr(current_user, "tier", "free") not in ("researcher", "professional")):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Upgrade to Researcher to download datasets.")
    
    # record usage
    metrics = db.query(UsageMetrics).filter(UsageMetrics.user_id == current_user.id).first()
    if not metrics:
        metrics = UsageMetrics(user_id=current_user.id)
        db.add(metrics)
    
    # Usage limit checks by tier
    tier = getattr(current_user, "tier", "free")
    tier_limits = {"free": 5, "researcher": 5000, "professional": float('inf')}
    current_limit = tier_limits.get(tier, 5)
    if metrics.api_calls >= current_limit:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=f"Usage limit exceeded ({current_limit} API calls/month). Upgrade your plan to continue.")
    
    metrics.api_calls += 1
    metrics.data_downloads += 1
    db.commit()
    # Fake link/ack
    if not any(item["id"] == dataset_id for item in catalog):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    return {"message": "Download started", "dataset_id": dataset_id}


@marketplace_router.post("/upload")
async def upload_dataset(file: UploadFile = File(...), current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    # Gate uploads to professional only
    if getattr(current_user, "tier", "free") != "professional":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Upgrade to Professional to upload and sell datasets.")
    # record usage
    metrics = db.query(UsageMetrics).filter(UsageMetrics.user_id == current_user.id).first()
    if not metrics:
        metrics = UsageMetrics(user_id=current_user.id)
        db.add(metrics)
    metrics.api_calls += 1
    db.commit()
    # In a real app, persist storage and create listing
    return {"message": "Upload received", "filename": file.filename}


