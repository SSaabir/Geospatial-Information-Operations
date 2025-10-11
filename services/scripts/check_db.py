from dotenv import load_dotenv
import os, json
from sqlalchemy import create_engine, text

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

u = os.getenv('DB_USER')
p = os.getenv('DB_PASSWORD')
h = os.getenv('DB_HOST', 'localhost')
port = os.getenv('DB_PORT', '5432')
dbname = os.getenv('DB_NAME')

if not all([u, p, h, port, dbname]):
    print('MISSING_DB_VARS', {'DB_USER': bool(u), 'DB_PASSWORD': bool(p), 'DB_HOST': h, 'DB_PORT': port, 'DB_NAME': dbname})
    raise SystemExit(1)

url = f'postgresql+psycopg2://{u}:{p}@{h}:{port}/{dbname}'
print('CONNECTING_TO', url.replace(p, '***'))

try:
    engine = create_engine(url)
    with engine.connect() as conn:
        exists = conn.execute(text("SELECT count(*) FROM information_schema.tables WHERE table_schema='public' AND table_name='weather_data'")).scalar()
        print('TABLE_EXISTS', bool(exists))
        if not exists:
            print('TABLE_MISSING')
        else:
            rc = conn.execute(text('SELECT COUNT(*) FROM weather_data')).scalar()
            print('ROW_COUNT', rc)
            rows = conn.execute(text('SELECT datetime::text as datetime, temp, statedistrict FROM weather_data ORDER BY datetime DESC LIMIT 5')).fetchall()
            out = []
            for row in rows:
                try:
                    out.append({k: row[k] for k in row.keys()})
                except Exception:
                    out.append(list(row))
            print('SAMPLE', json.dumps(out, default=str))
except Exception as e:
    print('CONNECT_ERROR', str(e))
