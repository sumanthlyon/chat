import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

#to read .env file
load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")

#engine -> connection pool
engine = create_engine(DATABASE_URL)

#session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)