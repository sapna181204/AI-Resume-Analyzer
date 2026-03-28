from sqlalchemy import create_engine

import os
from dotenv import load_dotenv

load_dotenv()  # load values from .env

DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_URL = f"postgresql://postgres:{DATABASE_PASSWORD}@localhost:5432/resume_ai_db"

engine = create_engine(DATABASE_URL)

try:
    connection = engine.connect()
    print("✅ Database connected successfully!")
    connection.close()
except Exception as e:
    print("❌ Connection failed:", e)