from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import Body
from pydantic import BaseModel
from . import models, schemas, crud
from .database import engine, get_db
from typing import List, Optional
from sqlalchemy import or_
from dotenv import load_dotenv
import os
import json
import re
import openai
from pydantic import BaseModel
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

openai.api_key = os.getenv("OPENAI_API_KEY")

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="LocalHub API")

# Serve frontend static files if they exist (Vite output `dist`)
from fastapi.staticfiles import StaticFiles
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DIST_DIR = os.path.join(BASE_DIR, "dist")
if os.path.isdir(DIST_DIR):
    app.mount("/", StaticFiles(directory=DIST_DIR, html=True), name="static")

class ChatRequest(BaseModel):
    message: str
    history: list | None = None
    region: str | None = None

def _detect_intent(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ("추천", "추천해", "가볼", "관광", "볼거리")):
        return "recommend_place"
    if any(k in t for k in ("축제", "공연", "일정", "기간")):
        return "festival_info"
    if any(k in t for k in ("맛집", "추천 음식", "음식점", "식당")):
        return "food_recommend"
    if any(k in t for k in ("게시글", "글", "커뮤니티", "포스트", "찾아")):
        return "search_post"
    return "general"

@app.post("/api/chat")
@app.post("/chat")
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    q = (req.message or "").strip()
    region = req.region
    intent = _detect_intent(q)

    # Retrieval: items + posts
    items = crud.search_items(db, q=q, region=region, limit=6)
    posts = crud.search_posts(db, q=q, category=None, limit=5)

    # Build context text for RAG
    item_snips = [f"{i.title} — {i.addr1 or ''}" for i in items]
    post_snips = [f"{p.title}: {(p.content or '')[:200]}" for p in posts]
    context_text = ""
    if items:
        context_text += "Items:\n" + "\n".join(item_snips) + "\n\n"
    if posts:
        context_text += "Posts:\n" + "\n".join(post_snips) + "\n\n"

    # Local quick answers for specific intents (no OpenAI)
    if intent == "recommend_place" and items:
        reply = "다음 지역 추천입니다:\n" + "\n".join(item_snips[:5])
        return {"reply": reply, "items": item_snips, "posts": post_snips, "intent": intent}
    if intent == "search_post" and posts:
        return {"reply": "관련 게시글을 찾았습니다.", "items": item_snips, "posts": post_snips, "intent": intent}

    # If OpenAI key is available, ask for a short answer using context
    if openai.api_key:
        system = "You are a helpful local guide assistant. Use provided sources to answer concisely."
        user_prompt = f"User query: {q}\n\nContext:\n{context_text}\n\nAnswer in Korean, short recommendations (title, address) or direct info."
        try:
            client = openai.OpenAI()
            resp = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {"role":"system","content":system},
                    {"role":"user","content":user_prompt}
                ],
                max_completion_tokens=300
            )
            reply = resp.choices[0].message.content.strip()
        except Exception as e:
            reply = "요청 처리 중 오류가 발생했습니다."
    else:
        # Fallback when OpenAI key missing
        if context_text:
            reply = "검색 결과가 있습니다:\n" + (context_text if len(context_text) < 1000 else context_text[:1000])
        else:
            reply = "죄송합니다. 현재 외부 요약 기능이 없습니다. 상세검색을 시도해 주세요."

    return {"reply": reply, "items": item_snips, "posts": post_snips, "intent": intent}

@app.post("/posts/{post_id}/like", response_model=schemas.PostOut)
@app.post("/api/posts/{post_id}/like", response_model=schemas.PostOut)
def like_post_endpoint(post_id: int, db: Session = Depends(get_db)):
    post = crud.like_post(db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

# 기존 /items 엔드포인트는 그대로
@app.get("/items", response_model=list[schemas.ItemOut])
def read_items(
    skip: int = 0,
    limit: int = 100,
    q: Optional[str] = None,
    region: Optional[str] = None,
    district: Optional[str] = None,
    category: Optional[str] = None,   # <-- 추가
    db: Session = Depends(get_db),
):
    query = db.query(models.Item)
    if q:
        query = query.filter(models.Item.title.contains(q))
    if region:
        query = query.filter((models.Item.region == region) | (models.Item.addr1.contains(region)))
    if district:
        query = query.filter(models.Item.addr1.contains(district))
    if category:
        # DB 컬럼은 models.Item.contentType에 저장되어 있으므로 동일성 비교
        query = query.filter(models.Item.contentType == category)
    return query.offset(skip).limit(limit).all()

@app.get("/items/{contentid}", response_model=schemas.ItemOut)
def read_item(contentid: str, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.contentid == contentid).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.get("/posts", response_model=list[schemas.PostOut])
def read_posts(skip: int = 0, limit: int = 100, q: Optional[str] = None, category: Optional[str] = None, db: Session = Depends(get_db)):
    return crud.get_posts(db, skip=skip, limit=limit, q=q, category=category)

@app.get("/posts/{post_id}", response_model=schemas.PostOut)
def read_post(post_id: int, db: Session = Depends(get_db)):
    post = crud.increment_views(db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.post("/posts/{post_id}/like", response_model=schemas.PostOut)
def like_post(post_id: int, db: Session = Depends(get_db)):
    post = crud.like_post(db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.post("/posts", response_model=schemas.PostOut)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    return crud.create_post(db, post=post)


@app.put("/posts/{post_id}", response_model=schemas.PostOut)
def update_post(post_id: int, body: dict = Body(...), db: Session = Depends(get_db)):
    # body: flat JSON from frontend, e.g. {"title": "...", "content": "...", "password": "..."}
    password = body.pop("password", None) or body.pop("edit_password", None)
    post_data = {k: v for k, v in body.items() if k in schemas.PostUpdate.__fields__}
    post_obj = schemas.PostUpdate(**post_data)
    try:
        updated = crud.update_post(db, post_id=post_id, post=post_obj, password=password)
    except PermissionError:
        raise HTTPException(status_code=403, detail="Password mismatch or not set")
    if not updated:
        raise HTTPException(status_code=404, detail="Post not found")
    return updated

@app.delete("/posts/{post_id}")
def delete_post(post_id: int, password: str = Body(..., embed=True), db: Session = Depends(get_db)):
    try:
        ok = crud.delete_post(db, post_id=post_id, password=password)
    except PermissionError:
        raise HTTPException(status_code=403, detail="Password mismatch or not set")
    if not ok:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"ok": True}

@app.get("/locations", response_model=list[schemas.ItemOut])
def search_locations(
    q: Optional[str] = Query(None, description="검색어"),
    gu: Optional[str] = Query(None, description="자치구 코드 또는 이름"),
    categories: Optional[str] = Query(None, description="쉼표구분 카테고리명(예: 관광지,쇼핑)"),
    limit: int = 500,
    db: Session = Depends(get_db)
):
    query = db.query(models.Item)
    if q:
        query = query.filter(models.Item.title.contains(q))
    if gu:
        gu_list = [g.strip() for g in gu.split(",") if g.strip()]
        if gu_list:
            query = query.filter(or_(*[
                or_(models.Item.sigungucode == g, models.Item.addr1.contains(g))
                for g in gu_list
            ]))
    if categories:
        cat_list = [c.strip() for c in categories.split(",") if c.strip()]
        if cat_list:
            query = query.filter(models.Item.contentType.in_(cat_list))
    return query.limit(limit).all()


from pydantic import BaseModel

class LocationDetail(schemas.ItemOut):
    related_posts: List[schemas.PostOut] = []

@app.get("/locations/{contentid}", response_model=LocationDetail)
def get_location(contentid: str, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.contentid == contentid).first()
    if not item:
        raise HTTPException(status_code=404, detail="Location not found")

    # 관련 게시글: 제목 또는 내용에 장소명 포함 (최대 3개)
    title = item.title or ""
    related = db.query(models.Post).filter(
        or_(models.Post.title.contains(title), models.Post.content.contains(title))
    ).limit(3).all()

    result = LocationDetail.from_orm(item)
    result.related_posts = related
    return result