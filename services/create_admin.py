
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.user import Base, UserDB
from db_config import DatabaseConfig
from security.jwt_handler import get_password_hash
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

def create_admin_user():
    """Create default admin user"""
    try:
        db_config = DatabaseConfig()
        db = db_config.get_session()
        
        # Check if admin user already exists
        existing_admin = db.query(UserDB).filter(UserDB.username == "admin").first()
        if existing_admin:
            print("✅ Admin user already exists!")
            return True
        
        # Create admin user with default credentials
        admin_user = UserDB(
            username="admin",
            email="admin@test.com",
            full_name="System Administrator",
            hashed_password=get_password_hash("password123"),
            is_active=True,
            is_admin=True,
            created_at=datetime.now(timezone.utc),
            avatar_url="https://api.dicebear.com/7.x/avataaars/svg?seed=admin"
        )
        
        db.add(admin_user)
        db.commit()
        
        print("✅ Admin user created successfully!")
        print("   Username: admin")
        print("   Password: password123")
        print("   Email: admin@test.com")
        return True
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        if 'db' in locals():
            db.rollback()
        return False
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    create_admin_user()