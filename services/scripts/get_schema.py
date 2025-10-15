"""Get current database schema for SQL file update"""
from db_config import DatabaseConfig
from sqlalchemy import text

db = DatabaseConfig()
engine = db.get_engine()
conn = engine.raw_connection()
cur = conn.cursor()

# Get all tables
cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    ORDER BY table_name
""")
tables = cur.fetchall()

print("\n" + "="*60)
print("CURRENT DATABASE TABLES")
print("="*60)
for table in tables:
    print(f"  • {table[0]}")

print("\n" + "="*60)
print("TABLE SCHEMAS")
print("="*60)

for table in tables:
    table_name = table[0]
    print(f"\n--- {table_name} ---")
    
    # Get columns for each table
    cur.execute("""
        SELECT 
            column_name, 
            data_type, 
            character_maximum_length,
            is_nullable,
            column_default
        FROM information_schema.columns 
        WHERE table_name = %s
        ORDER BY ordinal_position
    """, (table_name,))
    
    columns = cur.fetchall()
    for col in columns:
        col_name, data_type, max_len, nullable, default = col
        
        type_str = data_type
        if max_len:
            type_str += f"({max_len})"
        
        null_str = "" if nullable == "YES" else "NOT NULL"
        default_str = f"DEFAULT {default}" if default else ""
        
        print(f"  {col_name}: {type_str} {null_str} {default_str}".strip())

cur.close()
conn.close()

print("\n" + "="*60)
print("✅ Schema export complete!")
print("="*60)
