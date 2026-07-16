# backend/app/database.py (replace contents)
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 프로젝트 backend 폴더 기준으로 .env 경로를 명시적으로 지정
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOTENV_PATH = os.path.join(BASE_DIR, ".env")
if os.path.exists(DOTENV_PATH):
    load_dotenv(DOTENV_PATH)

# 기본값: backend 폴더에 localhub.db 파일을 생성하도록 절대경로 사용
default_db_path = os.path.abspath(os.path.join(BASE_DIR, "localhub.db"))
default_db_url = "sqlite:///" + default_db_path.replace(os.sep, "/")

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", default_db_url)

# sqlite의 경우 check_same_thread 옵션을 전달해야 함
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
