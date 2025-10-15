from typing import Dict, Optional
from models.usage import UsageMetrics
import logging

logger = logging.getLogger(__name__)


def tier_limits() -> Dict[str, float]:
    return {"free": 5, "researcher": 5000, "professional": float('inf')}


def get_limit_for_tier(tier: Optional[str]) -> float:
    return tier_limits().get(tier or "free", 5)


def has_quota(metrics: UsageMetrics, tier: Optional[str]) -> bool:
    limit = get_limit_for_tier(tier)
    if limit == float('inf'):
        return True
    return (metrics.api_calls or 0) < limit


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
