from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import get_settings

DATABASE_URL = (f"postgresql+psycopg://{get_settings().database_user}:{get_settings().database_password}"
                f"@{get_settings().database_host}:{get_settings().database_port}/{get_settings().database_name}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
