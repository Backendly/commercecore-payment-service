from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

Database_URL = os.getenv("DATABASE_URL")
engine = create_engine(Database_URL)
DBSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        db.close()
