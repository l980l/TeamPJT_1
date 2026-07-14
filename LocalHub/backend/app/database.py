# backend/app/database.py (replace contents)
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 프로젝트 backend 폴더 기준으로 .env 경로를 명시적으로 지정
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOTENV_PATH = os.path.join(BASE_DIR, ".env")
# load_dotenv에 경로를 직접 전달하면 find_dotenv() 관련 AssertionError 회피
if os.path.exists(DOTENV_PATH):
    load_dotenv(DOTENV_PATH)

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./localhub.db")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
