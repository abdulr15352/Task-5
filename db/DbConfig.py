from config import Settings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

settings = Settings()

# Postgres engine creation
def get_db_url():
    PORT = 5432
    return f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD.get_secret_value()}@{settings.POSTGRES_HOST}:{PORT}/{settings.POSTGRES_DB}"

Engine = create_engine(
    get_db_url(),
)

Base = declarative_base()
SessionLocal = sessionmaker(bind=Engine)



print("Database connected Successfully")

def get_db():
    """
    Dependency to get a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()