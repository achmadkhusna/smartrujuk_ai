#!/bin/sh
set -e

echo "Waiting for MySQL at ${DB_HOST}:${DB_PORT}..."

python - <<'PY'
import os, time
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

user = os.getenv("DB_USER", "root")
pw   = os.getenv("DB_PASSWORD", "")
host = os.getenv("DB_HOST", "db")
port = os.getenv("DB_PORT", "3306")
db   = os.getenv("DB_NAME", "smartrujuk_db")

url = f"mysql+mysqlconnector://{user}:{pw}@{host}:{port}/{db}"
engine = create_engine(url, pool_pre_ping=True)

for i in range(60):  # ~2 menit max
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("MySQL is ready.")
        break
    except OperationalError:
        time.sleep(2)
else:
    raise SystemExit("MySQL not ready after waiting.")

# Coba init schema kalau fungsi init_db tersedia & benar
try:
    from src.database import init_db
    init_db()
    print("init_db() executed.")
except Exception as e:
    print("init_db() skipped/failed:", e)
PY

exec streamlit run app.py --server.address=0.0.0.0 --server.port=8501
