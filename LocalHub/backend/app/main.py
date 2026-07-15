from typing import Optional
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import Body
from pydantic import BaseModel
from . import models, schemas, crud
from .database import engine, get_db
from dotenv import load_dotenv
import os
import re
import openai
from pydantic import BaseModel
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

openai.api_key = os.getenv("OPENAI_API_KEY")

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="LocalHub API")

class ChatRequest(BaseModel):
    message: str
    history: list | None = None
    region: str | None = None

@app.post("/api/chat")
@app.post("/chat")
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    q = req.message.strip()
    region = req.region

    # 1) 검색
    items = crud.search_items(db, q=q, region=region, limit=6)
    posts = crud.search_posts(db, q=q, category=None, limit=5)

    # 2) 바로 반환할 수준이면 검색결과 요약만 반환 (빠른 응답)
    if items or posts:
        item_snips = [f"{i.title} — {i.addr1 or ''}" for i in items]
        post_snips = [f"{p.title}: {(p.content or '')[:120]}" for p in posts]
        context_text = "Items:\n" + "\n".join(item_snips) + "\n\nPosts:\n" + "\n".join(post_snips)

        # 3) 필요하면 OpenAI에 요약/추천 요청
        prompt = (
            "You are LocalHub assistant. Use the sources below to answer the user query concisely.\n\n"
            f"User query: {q}\n\nSources:\n{context_text}\n\n"
            "Answer with short recommendations (title, address) and 1‑2 sentence summary."
        )

        if openai.api_key:
            client = openai.OpenAI()
            resp = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {"role":"system", "content":"You are a helpful assistant specialized in local info."},
                    {"role":"user", "content": prompt}
                ],
                max_completion_tokens=300
            )
            reply = resp.choices[0].message.content.strip()
        else:
            reply = "검색 결과를 찾았습니다. (OpenAI 키가 없어 요약은 제공되지 않습니다.)"

        return {"reply": reply, "items": item_snips, "posts": post_snips, "context_count": len(items)+len(posts)}
# --- end retrieval fallback; if no results, continue to OpenAI ---
    # 4) OpenAI ChatCompletion (간단 동기 호출)
    if not openai.api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not set on server")


    try:
        client = openai.OpenAI()
        resp = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role":"system","content":"You are a helpful assistant answering about local info."},
                {"role":"user","content": q}
            ],
            max_completion_tokens=500
        )
        reply = resp.choices[0].message.content.strip()
    except Exception as e:
        import traceback, sys
        traceback.print_exc(file=sys.stdout)
        raise HTTPException(status_code=500, detail=f"OpenAI call failed: {str(e)}")
    return {"reply": reply, "context_count": len(posts) + len(items)}

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