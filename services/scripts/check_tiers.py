import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from db_config import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

cursor.execute('SELECT id, username, tier FROM users ORDER BY id DESC LIMIT 10')
print('Recent users and their tiers:')
print('-' * 50)
for row in cursor.fetchall():
    print(f'ID: {row[0]}, Username: {row[1]}, Tier: {row[2]}')

cursor.close()
conn.close()
