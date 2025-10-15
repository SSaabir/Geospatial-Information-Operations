# Test Notification Panel
# This script creates test notifications for debugging

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.notification_manager import notify
from db_config import DatabaseConfig

def create_test_notifications():
    """Create test notifications for all users"""
    db_config = DatabaseConfig()
    engine = db_config.get_engine()
    
    # Get all user IDs
    from sqlalchemy import text
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, email FROM users LIMIT 5"))
        users = result.fetchall()
        
        print(f"Found {len(users)} users")
        
        for user in users:
            user_id, email = user
            print(f"\nCreating test notifications for user {email} (ID: {user_id})")
            
            # Create different types of test notifications
            notifications = [
                {
                    "subject": "Welcome to GeoWeather AI!",
                    "message": "Your account has been successfully set up. Explore weather analytics and predictions.",
                    "level": "info",
                    "user_id": user_id
                },
                {
                    "subject": "Weather Alert",
                    "message": "Heavy rainfall expected in your region within the next 24 hours.",
                    "level": "warning",
                    "user_id": user_id
                },
                {
                    "subject": "Subscription Active",
                    "message": "Your Professional tier subscription is now active. Enjoy all premium features!",
                    "level": "success",
                    "user_id": user_id
                },
                {
                    "subject": "System Update",
                    "message": "New weather prediction models have been deployed. Improved accuracy by 15%.",
                    "level": "info",
                    "user_id": user_id
                }
            ]
            
            for notif in notifications:
                try:
                    notify(
                        subject=notif["subject"],
                        message=notif["message"],
                        level=notif["level"],
                        metadata={"test": True, "user_id": user_id},
                        engine=engine
                    )
                    print(f"  ✅ Created: {notif['subject']}")
                except Exception as e:
                    print(f"  ❌ Failed: {notif['subject']} - {e}")
    
    print("\n✅ Test notifications created successfully!")

if __name__ == "__main__":
    create_test_notifications()
