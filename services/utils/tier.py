from typing import Dict, Optional
from datetime import datetime, timedelta, date
from models.usage import UsageMetrics
import logging

logger = logging.getLogger(__name__)


# ===== API CALL QUOTAS =====
def tier_limits() -> Dict[str, float]:
    return {"free": 5, "researcher": 5000, "professional": float('inf')}


def get_limit_for_tier(tier: Optional[str]) -> float:
    return tier_limits().get(tier or "free", 5)


def has_quota(metrics: UsageMetrics, tier: Optional[str]) -> bool:
    limit = get_limit_for_tier(tier)
    if limit == float('inf'):
        return True
    return (metrics.api_calls or 0) < limit


# ===== HISTORICAL DATA ACCESS LIMITS =====
def historical_access_limits() -> Dict[str, float]:
    """Return days of historical data access by tier.
    
    Returns:
        dict: Days of historical data access for each tier
            - free: 30 days (last month)
            - researcher: 365 days (last year)
            - professional: unlimited (full 28 years from 1997)
    """
    return {
        "free": 30,                # Last 30 days
        "researcher": 365,         # Last 1 year
        "professional": float('inf')  # Unlimited (all 28 years)
    }


def get_historical_days_for_tier(tier: Optional[str]) -> float:
    """Get maximum days of historical data accessible for a tier.
    
    Args:
        tier: User's subscription tier ('free', 'researcher', 'professional')
        
    Returns:
        float: Number of days of historical data access (inf for unlimited)
    """
    limits = historical_access_limits()
    return limits.get(tier or "free", 30)


def enforce_historical_access(requested_date: date, user_tier: Optional[str]):
    """Enforce historical data access limits based on user tier.
    
    Raises HTTPException if requested date exceeds tier's historical access limit.
    
    Args:
        requested_date: The date being requested
        user_tier: User's subscription tier
        
    Raises:
        HTTPException: 403 if date is beyond tier's access limit
    """
    from fastapi import HTTPException, status
    
    max_days = get_historical_days_for_tier(user_tier)
    
    # Professional tier has unlimited access
    if max_days == float('inf'):
        return
    
    # Calculate oldest accessible date
    oldest_allowed = date.today() - timedelta(days=int(max_days))
    
    # Check if requested date is too old
    if requested_date < oldest_allowed:
        tier_name = user_tier or "free"
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Historical data access limit exceeded",
                "message": f"Your {tier_name.capitalize()} plan allows access to the last {int(max_days)} days of data only.",
                "oldest_accessible_date": oldest_allowed.isoformat(),
                "requested_date": requested_date.isoformat(),
                "upgrade_required": "researcher" if tier_name == "free" else "professional",
                "upgrade_benefits": "Upgrade to access more historical data: Researcher (1 year), Professional (full 28 years since 1997)"
            }
        )


def check_and_notify_usage(metrics: UsageMetrics, tier: Optional[str], user_id: int, username: str = "User"):
    """
    Check usage and send notifications at various thresholds:
    - 50% used: Info notification
    - 75% used: Warning notification
    - 90% used: Urgent warning notification
    
    Returns the usage ratio (0.0 to 1.0+)
    """
    limit = get_limit_for_tier(tier)
    
    # Professional tier has unlimited
    if limit == float('inf'):
        return 0.0
    
    usage_ratio = (metrics.api_calls or 0) / limit
    
    try:
        from utils.notification_manager import notify
        
        # 90% threshold - Urgent warning
        if usage_ratio >= 0.9 and usage_ratio < 1.0:
            notify(
                subject="⚠️ Usage Nearing Limit",
                message=f"You've used {metrics.api_calls} of {limit} API calls ({int(usage_ratio*100)}%). Upgrade to avoid service interruption.",
                level='warning',
                metadata={
                    'user_id': user_id,
                    'username': username,
                    'api_calls': metrics.api_calls,
                    'limit': limit,
                    'usage_percentage': int(usage_ratio * 100),
                    'tier': tier or 'free'
                },
                user_id=user_id
            )
            logger.warning(f"User {username} (ID: {user_id}) at 90% usage: {metrics.api_calls}/{limit}")
        
        # 75% threshold - Warning
        elif usage_ratio >= 0.75 and usage_ratio < 0.9:
            notify(
                subject="📊 Usage Alert",
                message=f"You've used {metrics.api_calls} of {limit} API calls ({int(usage_ratio*100)}%). Consider upgrading your plan.",
                level='info',
                metadata={
                    'user_id': user_id,
                    'username': username,
                    'api_calls': metrics.api_calls,
                    'limit': limit,
                    'usage_percentage': int(usage_ratio * 100),
                    'tier': tier or 'free'
                },
                user_id=user_id
            )
            logger.info(f"User {username} (ID: {user_id}) at 75% usage: {metrics.api_calls}/{limit}")
        
        # 50% threshold - Info
        elif usage_ratio >= 0.5 and usage_ratio < 0.75:
            notify(
                subject="📈 Usage Update",
                message=f"You've used {metrics.api_calls} of {limit} API calls ({int(usage_ratio*100)}%). You're halfway to your limit.",
                level='info',
                metadata={
                    'user_id': user_id,
                    'username': username,
                    'api_calls': metrics.api_calls,
                    'limit': limit,
                    'usage_percentage': int(usage_ratio * 100),
                    'tier': tier or 'free'
                },
                user_id=user_id
            )
            logger.info(f"User {username} (ID: {user_id}) at 50% usage: {metrics.api_calls}/{limit}")
    
    except Exception as e:
        logger.error(f"Failed to send usage notification: {e}")
    
    return usage_ratio


def enforce_quota_or_raise(metrics: UsageMetrics, tier: Optional[str], user_id: Optional[int] = None, username: str = "User"):
    """
    Enforce quota limits and raise HTTPException if exceeded.
    Sends error notification when quota is exceeded.
    """
    if not has_quota(metrics, tier):
        from fastapi import HTTPException, status

        limit = get_limit_for_tier(tier)
        
        # Send notification when quota exceeded
        try:
            from utils.notification_manager import notify
            notify(
                subject="🚫 API Quota Exceeded",
                message=f"You've reached your limit of {limit} API calls this month. Upgrade your plan to continue using the service.",
                level='error',
                metadata={
                    'user_id': user_id,
                    'username': username,
                    'api_calls': metrics.api_calls,
                    'limit': limit,
                    'tier': tier or 'free',
                    'action_required': 'upgrade_plan'
                },
                user_id=user_id
            )
            logger.error(f"User {username} (ID: {user_id}) quota exceeded: {metrics.api_calls}/{limit}")
        except Exception as e:
            logger.error(f"Failed to send quota exceeded notification: {e}")
        
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, 
            detail=f"Usage limit exceeded ({limit} API calls/month). Upgrade your plan to continue."
        )
