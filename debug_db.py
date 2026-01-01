import sys
import os
sys.path.append(os.getcwd())
from app.models import init_db, engine
from sqlalchemy import text

print("Attempting to connect...")
with engine.connect() as conn:
    print("Connected. Testing vector extension...")
    try:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
        print("Vector extension confirmed.")
    except Exception as e:
        print(f"Error checking extension: {e}")

print("Attempting to create tables...")
try:
    init_db()
    print("Tables created successfully.")
except Exception as e:
    print(f"FAILED: {e}")
