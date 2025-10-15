"""API endpoints for user notifications"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
from sqlalchemy import text

from security.auth_middleware import verify_token
from db_config import DatabaseConfig

notifications_router = APIRouter(prefix="/notifications", tags=["notifications"])


def get_db():
    """Dependency to get database connection"""
    db_config = DatabaseConfig()
    engine = db_config.get_engine()
    return engine


@notifications_router.get("/user")
async def get_user_notifications(
    user_data: Dict[str, Any] = Depends(verify_token),
    db=Depends(get_db),
    level: Optional[str] = None,
    limit: int = 50,
    unread_only: bool = False
):
    """Get notifications for the authenticated user"""
    try:
        user_id = user_data.get("user_id") or user_data.get("id")
        
        with db.connect() as conn:
            # Build query with filters - only show user-specific notifications
            query = """
                SELECT 
                    id, 
                    timestamp, 
                    level, 
                    subject, 
                    message, 
                    metadata,
                    read,
                    user_id
                FROM notifications 
                WHERE user_id = :user_id
            """
            params = {"user_id": user_id, "limit": limit}
            
            if level:
                query += " AND level = :level"
                params["level"] = level
            
            if unread_only:
                query += " AND read = false"
            
            query += " ORDER BY timestamp DESC LIMIT :limit"
            
            result = conn.execute(text(query), params)
            notifications = []
            
            for row in result:
                # Parse metadata from JSONB
                metadata = row[5] if row[5] else {}
                if isinstance(metadata, str):
                    metadata = json.loads(metadata)
                
                notifications.append({
                    "id": row[0],
                    "timestamp": row[1].isoformat() if row[1] else None,
                    "level": row[2],
                    "subject": row[3],
                    "message": row[4],
                    "metadata": metadata,
                    "read": row[6] if row[6] is not None else False,
                    "user_id": row[7]
                })
            
            return {
                "notifications": notifications,
                "total": len(notifications)
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch notifications: {str(e)}")


@notifications_router.get("/unread-count")
async def get_unread_count(
    user_data: Dict[str, Any] = Depends(verify_token),
    db=Depends(get_db)
):
    """Get count of unread notifications for the user"""
    try:
        user_id = user_data.get("user_id") or user_data.get("id")
        
        with db.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT COUNT(*) 
                    FROM notifications 
                    WHERE user_id = :user_id 
                    AND read = false
                """),
                {"user_id": user_id}
            )
            count = result.scalar()
            
            return {"unread_count": count or 0}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to count unread notifications: {str(e)}")


@notifications_router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    user_data: Dict[str, Any] = Depends(verify_token),
    db=Depends(get_db)
):
    """Mark a notification as read"""
    try:
        user_id = user_data.get("user_id") or user_data.get("id")
        
        with db.connect() as conn:
            # Check if notification exists and belongs to user
            check_result = conn.execute(
                text("""
                    SELECT id FROM notifications 
                    WHERE id = :notification_id 
                    AND user_id = :user_id
                """),
                {"notification_id": notification_id, "user_id": user_id}
            )
            
            if not check_result.fetchone():
                raise HTTPException(status_code=404, detail="Notification not found")
            
            # Mark as read
            conn.execute(
                text("""
                    UPDATE notifications 
                    SET read = true 
                    WHERE id = :notification_id
                """),
                {"notification_id": notification_id}
            )
            conn.commit()
            
            return {"message": "Notification marked as read", "notification_id": notification_id}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark notification as read: {str(e)}")


@notifications_router.put("/read-all")
async def mark_all_read(
    user_data: Dict[str, Any] = Depends(verify_token),
    db=Depends(get_db)
):
    """Mark all notifications as read for the user"""
    try:
        user_id = user_data.get("user_id") or user_data.get("id")
        
        with db.connect() as conn:
            result = conn.execute(
                text("""
                    UPDATE notifications 
                    SET read = true 
                    WHERE user_id = :user_id 
                    AND read = false
                """),
                {"user_id": user_id}
            )
            conn.commit()
            
            return {
                "message": "All notifications marked as read",
                "updated_count": result.rowcount
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark all as read: {str(e)}")


@notifications_router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    user_data: Dict[str, Any] = Depends(verify_token),
    db=Depends(get_db)
):
    """Delete a notification"""
    try:
        user_id = user_data.get("user_id") or user_data.get("id")
        
        with db.connect() as conn:
            # Check if notification exists and belongs to user
            check_result = conn.execute(
                text("""
                    SELECT id FROM notifications 
                    WHERE id = :notification_id 
                    AND user_id = :user_id
                """),
                {"notification_id": notification_id, "user_id": user_id}
            )
            
            if not check_result.fetchone():
                raise HTTPException(status_code=404, detail="Notification not found")
            
            # Delete notification
            conn.execute(
                text("DELETE FROM notifications WHERE id = :notification_id"),
                {"notification_id": notification_id}
            )
            conn.commit()
            
            return {"message": "Notification deleted", "notification_id": notification_id}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete notification: {str(e)}")


@notifications_router.post("/test")
async def create_test_notification(
    user_data: Dict[str, Any] = Depends(verify_token),
    db=Depends(get_db)
):
    """Create a test notification for the user (for testing purposes)"""
    try:
        from utils.notification_manager import notify
        
        user_id = user_data.get("user_id") or user_data.get("id")
        
        notify(
            subject="Test Notification",
            message="This is a test notification from the system.",
            level="info",
            metadata={"test": True, "user_id": user_id},
            engine=db
        )
        
        return {"message": "Test notification created"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create test notification: {str(e)}")
