"""Quick script to create test notifications for current user"""
import sys
from db_config import DatabaseConfig
from sqlalchemy import text

def create_test_notifications(user_id: int):
    db = DatabaseConfig()
    engine = db.get_engine()
    conn = engine.connect()
    
    try:
        # Create some test notifications
        notifications = [
            {
                'user_id': user_id,
                'subject': 'Welcome!',
                'message': 'Welcome to GeoWeather AI Platform',
                'level': 'info',
                'read': False
            },
            {
                'user_id': user_id,
                'subject': 'Weather Alert',
                'message': 'High temperatures expected in your region',
                'level': 'warning',
                'read': False
            },
            {
                'user_id': user_id,
                'subject': 'System Update',
                'message': 'New features available in the weather predictor',
                'level': 'success',
                'read': False
            }
        ]
        
        for notif in notifications:
            query = text("""
                INSERT INTO notifications (user_id, subject, message, level, read, timestamp)
                VALUES (:user_id, :subject, :message, :level, :read, NOW())
            """)
            conn.execute(query, notif)
        
        conn.commit()
        print(f"✅ Created 3 test notifications for user {user_id}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_test_notif.py <user_id>")
        print("\nTo get your user ID, run: python check_users.py")
        sys.exit(1)
    
    user_id = int(sys.argv[1])
    create_test_notifications(user_id)
