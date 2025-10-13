import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from db_config import DatabaseConfig
from sqlalchemy import text

db = DatabaseConfig()
engine = db.get_engine()

with engine.connect() as conn:
    print("=== NOTIFICATIONS TABLE STRUCTURE ===")
    cols = conn.execute(text("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'notifications' 
        ORDER BY ordinal_position
    """)).fetchall()
    
    for col in cols:
        print(f"  {col[0]}: {col[1]}")
    
    print("\n=== NOTIFICATIONS COUNT ===")
    total = conn.execute(text("SELECT COUNT(*) FROM notifications")).scalar()
    print(f"Total notifications: {total}")
    
    # Count by user
    print("\n=== NOTIFICATIONS BY USER ===")
    by_user = conn.execute(text("""
        SELECT user_id, COUNT(*) as count, 
               SUM(CASE WHEN read = true THEN 1 ELSE 0 END) as read_count,
               SUM(CASE WHEN read = false THEN 1 ELSE 0 END) as unread_count
        FROM notifications 
        GROUP BY user_id 
        ORDER BY count DESC
    """)).fetchall()
    
    for row in by_user:
        print(f"  User {row[0]}: {row[1]} total ({row[2]} read, {row[3]} unread)")
    
    # Count notifications without user_id (system-wide)
    print("\n=== SYSTEM-WIDE NOTIFICATIONS (user_id IS NULL) ===")
    system_count = conn.execute(text("""
        SELECT COUNT(*) FROM notifications WHERE user_id IS NULL
    """)).scalar()
    print(f"System-wide notifications: {system_count}")
    
    print("\n=== SAMPLE NOTIFICATIONS ===")
    rows = conn.execute(text("""
        SELECT id, user_id, level, subject, read, timestamp::text 
        FROM notifications 
        ORDER BY timestamp DESC 
        LIMIT 10
    """)).fetchall()
    
    for row in rows:
        user_info = f"User {row[1]}" if row[1] else "SYSTEM-WIDE"
        read_status = "✓ Read" if row[4] else "○ Unread"
        print(f"  [{row[5]}] {user_info} | {row[2]} | {row[3]} | {read_status}")
