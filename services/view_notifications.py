"""View notifications from the database"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from db_config import DatabaseConfig
from sqlalchemy import text
from datetime import datetime
import json

def view_notifications(limit=50, level=None):
    """View recent notifications from the database"""
    db_config = DatabaseConfig()
    engine = db_config.get_engine()
    
    with engine.connect() as conn:
        # Check if table exists
        try:
            result = conn.execute(text("SELECT COUNT(*) FROM notifications"))
            count = result.scalar()
            print(f"\n📊 Total notifications in database: {count}\n")
        except Exception as e:
            print(f"❌ Error: Notifications table might not exist yet: {e}")
            print("\nTo create the table, send a notification:")
            print("  python -c \"from utils.notification_manager import notify; notify('Test', 'Test message')\"")
            return
        
        # Build query
        query = "SELECT * FROM notifications"
        if level:
            query += f" WHERE level = :level"
        query += " ORDER BY timestamp DESC LIMIT :limit"
        
        # Execute query
        params = {'limit': limit}
        if level:
            params['level'] = level
            
        result = conn.execute(text(query), params)
        rows = result.fetchall()
        
        if not rows:
            print("No notifications found.")
            return
        
        # Display notifications
        print("=" * 100)
        for row in rows:
            # Handle different ways the row might be structured
            if hasattr(row, '_mapping'):
                data = dict(row._mapping)
            else:
                data = dict(row)
            
            level_emoji = {
                'info': 'ℹ️',
                'warning': '⚠️',
                'error': '❌',
                'critical': '🚨'
            }.get(data.get('level', 'info'), 'ℹ️')
            
            print(f"\n{level_emoji} [{data.get('level', 'info').upper()}] {data.get('subject', 'N/A')}")
            print(f"   Time: {data.get('timestamp', 'N/A')}")
            print(f"   Message: {data.get('message', 'N/A')}")
            
            # Parse and display metadata
            metadata = data.get('metadata')
            if metadata:
                if isinstance(metadata, str):
                    try:
                        metadata = json.loads(metadata)
                    except:
                        pass
                if isinstance(metadata, dict) and metadata:
                    print(f"   Metadata: {json.dumps(metadata, indent=14)}")
            
            print("-" * 100)

def view_by_level():
    """View notifications grouped by level"""
    db_config = DatabaseConfig()
    engine = db_config.get_engine()
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT level, COUNT(*) as count 
            FROM notifications 
            GROUP BY level 
            ORDER BY count DESC
        """))
        
        print("\n📈 Notifications by Level:")
        print("-" * 40)
        for row in result:
            level = row[0] if hasattr(row, '__getitem__') else row.level
            count = row[1] if hasattr(row, '__getitem__') else row.count
            emoji = {'info': 'ℹ️', 'warning': '⚠️', 'error': '❌', 'critical': '🚨'}.get(level, 'ℹ️')
            print(f"{emoji} {level.upper():<10} : {count}")

def view_recent_payments():
    """View recent payment-related notifications"""
    db_config = DatabaseConfig()
    engine = db_config.get_engine()
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT * FROM notifications 
            WHERE subject LIKE '%Payment%' OR subject LIKE '%payment%'
            ORDER BY timestamp DESC 
            LIMIT 20
        """))
        
        rows = result.fetchall()
        if not rows:
            print("\n💰 No payment notifications found.")
            return
        
        print("\n💰 Recent Payment Notifications:")
        print("=" * 100)
        for row in rows:
            if hasattr(row, '_mapping'):
                data = dict(row._mapping)
            else:
                data = dict(row)
            
            print(f"\n   {data.get('subject', 'N/A')}")
            print(f"   Time: {data.get('timestamp', 'N/A')}")
            print(f"   {data.get('message', 'N/A')}")
            print("-" * 100)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='View notifications from database')
    parser.add_argument('--limit', type=int, default=50, help='Number of notifications to show')
    parser.add_argument('--level', type=str, choices=['info', 'warning', 'error', 'critical'], help='Filter by level')
    parser.add_argument('--payments', action='store_true', help='Show only payment notifications')
    parser.add_argument('--stats', action='store_true', help='Show notification statistics')
    
    args = parser.parse_args()
    
    try:
        if args.stats:
            view_by_level()
        elif args.payments:
            view_recent_payments()
        else:
            view_notifications(limit=args.limit, level=args.level)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
