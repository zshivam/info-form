from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables from a .env file (only needed for local dev)
load_dotenv()

# Get the full database URL (defined in Railway dashboard)
DATABASE_URL = os.getenv("DATABASE_URL")

# Check if DATABASE_URL is actually set (good for debugging)
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set. Make sure it's defined in the environment.")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()
