
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

# Locate the existing backend/.env file
PROJECT_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_DIR / "backend" / ".env"

load_dotenv(ENV_FILE)

# Read database configuration
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Validate configuration
if not all([DB_HOST, DB_PORT, DB_NAME, DB_USER]) or DB_PASSWORD is None:
    raise ValueError("Database configuration is incomplete. Check backend/.env")

# Create connection URL
DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME
)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

# Test database connection
def test_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT DATABASE()"))
        database_name = result.scalar_one()

    print("Database connection successful!")
    print("Connected database:", database_name)


if __name__ == "__main__":
    test_connection()
