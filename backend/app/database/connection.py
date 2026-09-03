import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv


# Load DigiLaw .env file
BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        ".."
    )
)

load_dotenv(
    os.path.join(
        BASE_DIR,
        ".env"
    )
)


# PostgreSQL settings
DB_USER = os.getenv(
    "POSTGRES_USER",
    "postgres"
)

DB_PASSWORD = os.getenv(
    "POSTGRES_PASSWORD"
)

DB_HOST = os.getenv(
    "POSTGRES_HOST",
    "localhost"
)

DB_PORT = os.getenv(
    "POSTGRES_PORT",
    "5432"
)

DB_NAME = os.getenv(
    "POSTGRES_DB",
    "digilaw_db"
)


# Make sure password exists
if not DB_PASSWORD:
    raise ValueError(
        "POSTGRES_PASSWORD was not found in .env"
    )


# PostgreSQL connection URL
DATABASE_URL = (
    f"postgresql+psycopg://"
    f"{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}"
    f"/{DB_NAME}"
)


# SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    echo=False
)


# Database session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# FastAPI database dependency
def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()