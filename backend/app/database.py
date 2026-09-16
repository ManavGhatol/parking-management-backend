import os
# pyrefly: ignore [missing-import]
from sqlalchemy import create_engine
# pyrefly: ignore [missing-import]
from sqlalchemy.ext.declarative import declarative_base
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import sessionmaker
# pyrefly: ignore [missing-import]
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

# Database Setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./parking.db")

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)
    
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# MongoDB Setup
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
mongo_client = AsyncIOMotorClient(MONGODB_URL)
mongo_db = mongo_client.parking_audit_db

def get_mongo_db():
    return mongo_db
