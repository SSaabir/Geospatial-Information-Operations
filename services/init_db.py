import sys
import os
import argparse
from datetime import datetime, timezone

# Add the services directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.user import Base, UserDB
from db_config import DatabaseConfig
from security.jwt_handler import get_password_hash
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_tables():
    """Create all database tables"""
    try:
        db_config = DatabaseConfig()
        engine = db_config.get_engine()
        
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        return False

def create_admin_user():
    """Create an admin user"""
    try:
        db_config = DatabaseConfig()
        db = db_config.get_session()
        
        # Check if admin user already exists
        existing_admin = db.query(UserDB).filter(UserDB.username == "admin").first()
        if existing_admin:
            print("ℹ️  Admin user already exists!")
            return True
        
        # Get admin credentials
        print("\n📝 Creating admin user...")
        username = input("Enter admin username (default: admin): ").strip() or "admin"
        email = input("Enter admin email: ").strip()
        
        if not email:
            print("❌ Email is required!")
            return False
        
        while True:
            password = input("Enter admin password (min 8 characters): ").strip()
            if len(password) >= 8:
                break
            print("❌ Password must be at least 8 characters!")
        
        confirm_password = input("Confirm admin password: ").strip()
        if password != confirm_password:
            print("❌ Passwords do not match!")
            return False
        
        full_name = input("Enter admin full name (optional): ").strip() or "System Administrator"
        
        # Create admin user
        admin_user = UserDB(
            username=username,
            email=email,
            full_name=full_name,
            hashed_password=get_password_hash(password),
            is_active=True,
            is_admin=True,
            created_at=datetime.now(timezone.utc),
            avatar_url=f"https://api.dicebear.com/7.x/avataaars/svg?seed={username}"
        )
        
        db.add(admin_user)
        db.commit()
        
        print(f"✅ Admin user '{username}' created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        if 'db' in locals():
            db.rollback()
        return False
    finally:
        if 'db' in locals():
            db.close()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Initialize the database for Geospatial Information Operations")
    parser.add_argument("--create-admin", action="store_true", help="Create an admin user after creating tables")
    
    args = parser.parse_args()
    
    print("🚀 Initializing Geospatial Information Operations Database")
    print("=" * 60)
    
    # Create tables
    if not create_tables():
        sys.exit(1)
    
    # Create admin user if requested
    if args.create_admin:
        print("\n" + "=" * 60)
        if not create_admin_user():
            sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 Database initialization completed successfully!")
    
    if not args.create_admin:
        print("\n💡 Tip: Run with --create-admin to create an admin user")

if __name__ == "__main__":
    main()