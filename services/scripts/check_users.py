"""
Script to check users table and their admin status
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_config import DatabaseConfig
from models.user import UserDB
from sqlalchemy import text

def check_users():
    db_config = DatabaseConfig()
    engine = db_config.get_engine()
    
    with engine.connect() as conn:
        # Check if users table exists
        result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')"))
        table_exists = result.scalar()
        print(f"Users table exists: {table_exists}")
        
        if table_exists:
            # Get all users with their admin status
            result = conn.execute(text("""
                SELECT id, username, email, is_admin, is_active, tier, created_at, last_login 
                FROM users 
                ORDER BY id
            """))
            users = result.fetchall()
            
            print(f"\nTotal users: {len(users)}")
            print("\n" + "="*100)
            for user in users:
                print(f"ID: {user[0]:3} | Username: {user[1]:20} | Email: {user[2]:30} | Admin: {user[3]} | Active: {user[4]} | Tier: {user[5]:12} | Last Login: {user[7]}")
            print("="*100)

if __name__ == "__main__":
    check_users()
