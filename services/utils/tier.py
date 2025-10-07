from typing import Dict, Optional
from models.usage import UsageMetrics


def tier_limits() -> Dict[str, float]:
    return {"free": 5, "researcher": 5000, "professional": float('inf')}


def get_limit_for_tier(tier: Optional[str]) -> float:
    return tier_limits().get(tier or "free", 5)


def has_quota(metrics: UsageMetrics, tier: Optional[str]) -> bool:
    limit = get_limit_for_tier(tier)
    if limit == float('inf'):
        return True
    return (metrics.api_calls or 0) < limit


def enforce_quota_or_raise(metrics: UsageMetrics, tier: Optional[str]):
    if not has_quota(metrics, tier):
        from fastapi import HTTPException, status

        limit = get_limit_for_tier(tier)
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=f"Usage limit exceeded ({limit} API calls/month). Upgrade your plan to continue.")
