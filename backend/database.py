from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

DB_URL = os.getenv("DATABASE_URL", "sqlite:///./data/app.db")

# Necessary for multithreading
e_args = {}
if "sqlite" in DB_URL:
    e_args["check_same_thread"] = False

# Start up the database connection and session
engine = create_engine(DB_URL, connect_args=e_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    # yield a db session
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
