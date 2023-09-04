from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.settings import get_db_url

engine = create_engine(get_db_url(), pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
