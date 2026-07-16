# backend/app/database.py (replace contents)
import os
import sys
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

# Prefer explicit Render/host env var if present, then standard DATABASE_URL
SQLALCHEMY_DATABASE_URL = os.getenv("RENDER_DATABASE_URL") or os.getenv("DATABASE_URL") or default_db_url

# Some platforms (and older libraries) provide a URL starting with "postgres://";
# SQLAlchemy expects the modern "postgresql://" scheme for the psycopg2 driver.
if SQLALCHEMY_DATABASE_URL and SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# sqlite의 경우 check_same_thread 옵션을 전달해야 함
try:
    if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
        engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
except Exception as e:
    # surface a helpful message during startup so Render logs show DB driver/connect issues
    print("DB connection error while creating engine:", e, file=sys.stderr)
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
