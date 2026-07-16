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
import random
from pydantic import BaseModel
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

openai.api_key = os.getenv("OPENAI_API_KEY")

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="LocalHub API")

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

@app.post("/chat")
# Replace chat(...) with this debug version (temporary)
@app.post("/api/chat")
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    import json, sys
    q = (req.message or "").strip()
    region = req.region
    print("DEBUG /api/chat incoming:", q, "region:", region, file=sys.stdout)

    # intent detection (same as before)
    def _detect_intent(text: str) -> str:
        t = (text or "").lower()
        if any(k in t for k in ("추천","가볼","관광","볼거리")): return "recommend_place"
        if any(k in t for k in ("축제","공연","일정","기간")): return "festival_info"
        if any(k in t for k in ("맛집","음식점","식당")): return "food_recommend"
        if any(k in t for k in ("게시글","글","커뮤니티","포스트","찾아")): return "search_post"
        return "general"

    intent = _detect_intent(q)
    # detect possible category keywords in the user's message (simple heuristics)
    category_token = None
    category_keywords = ['쇼핑', '숙박', '여행코스', '여행', '축제', '레포츠', '문화', '맛집', '카페']
    for kw in category_keywords:
        if kw in (q or ""):
            category_token = kw
            break

    # Map simple keywords to contentType substrings stored in DB (expanded synonyms)
    category_map = {
        '숙박': '숙박', '호텔': '숙박', '게스트하우스': '숙박',
        '쇼핑': '쇼핑', '몰': '쇼핑', '아울렛': '쇼핑',
        '여행코스': '여행코스', '여행': '여행코스', '코스': '여행코스',
        '축제': '축제', '페스티벌': '축제',
        '레포츠': '레포츠', '레저': '레포츠',
        '문화': '문화', '미술관': '문화', '박물관': '문화',
        '맛집': '음식', '음식': '음식', '레스토랑': '음식',
        '카페': '카페', '디저트': '카페'
    }
    category_filter = category_map.get(category_token)

    # detect region by checking addr1 values in DB when a token looks like a place name
    region_guess = None
    region_tokens = []
    # extract all hangul tokens
    toks = re.findall(r'[가-힣]+', q or '')
    # build dynamic region candidates from DB addr1 (take first token of addr1 values)
    region_candidates = set([
    '강남', '강동', '강북', '강서', '관악', 
    '광진', '구로', '금천', '노원', '도봉', 
    '동대문', '동작', '마포', '서대문', '서초', 
    '성동', '성북', '송파', '양천', '영등포', 
    '용산', '은평', '종로', '중', '중랑'
    ])
    try:
        # load all distinct addr1 values and extract Korean tokens (e.g., '강남구','종로구','서초동')
        rows = db.query(models.Item.addr1).distinct().all()
        for (addr1,) in rows:
            if not addr1:
                continue
            # find hangul tokens in addr1
            tokens = re.findall(r'[가-힣]+', addr1)
            for tk in tokens:
                if len(tk) > 1:
                    region_candidates.add(tk)
    except Exception:
        pass
    for t in toks:
        if t in region_candidates:
            region_tokens.append(t)
    # if we have candidates, verify against DB addr1
    if region_tokens:
        for rc in region_tokens:
            try:
                cnt = db.query(models.Item).filter(models.Item.addr1.contains(rc)).count()
                if cnt > 0:
                    region_guess = rc
                    break
            except Exception:
                continue
    # if still no region_guess, try to infer from DB by searching the query in title
    if not region_guess and q:
        try:
            sample = db.query(models.Item).filter(models.Item.title.contains(q)).first()
            if sample and sample.addr1:
                # use the administrative area (addr1) as region
                region_guess = sample.addr1
        except Exception:
            region_guess = None
    print("DEBUG intent:", intent, file=sys.stdout)

    # retrieval (prefer category-aware search when detected). Use region_guess and category_filter.
    try:
        # fetch more results from DB so we can randomly pick up to 3 matches
        items = crud.search_items(db, q=q, region=region_guess or region, category=category_filter, limit=50)
        # fallback: if category filter returned nothing, try region-only search and filter by contentType/title
        if (not items) and category_filter and (region_guess or region):
            try:
                alt = crud.search_items(db, q=None, region=region_guess or region, category=None, limit=50)
                filtered = []
                for it in alt:
                    ct = getattr(it, 'contentType', '') or ''
                    title = getattr(it, 'title', '') or ''
                    if category_filter and category_filter in ct:
                        filtered.append(it)
                    elif category_token and category_token in title:
                        filtered.append(it)
                if filtered:
                    items = filtered
                    print('DEBUG fallback matched items by region+heuristic:', len(items), file=sys.stdout)
            except Exception:
                pass
            # If still no items, try matching distinct contentType values (substring/fuzzy)
            if not items:
                try:
                    cts = [r[0] for r in db.query(models.Item.contentType).distinct().all() if r[0]]
                    matches = []
                    for ct in cts:
                        if not ct: continue
                        if category_token and category_token in ct:
                            matches.append(ct)
                        elif category_token and ct in category_token:
                            matches.append(ct)
                        else:
                            # loose match: share at least 2 characters
                            common = set(ct) & set(category_token or '')
                            if len(common) >= 2:
                                matches.append(ct)
                    if matches:
                        # search using each matched contentType and collect
                        combined = []
                        for mct in matches:
                            try:
                                found = db.query(models.Item).filter(models.Item.contentType.contains(mct))
                                if region_guess or region:
                                    found = found.filter(models.Item.addr1.contains(region_guess or region))
                                combined.extend(found.limit(50).all())
                            except Exception:
                                continue
                        if combined:
                            items = combined
                            print('DEBUG fallback matched items by contentType synonyms:', len(items), file=sys.stdout)
                except Exception:
                    pass
        # also search posts (no category filtering for posts yet)
        posts = crud.search_posts(db, q=q, category=None, limit=5)
    except Exception as e:
        print("DEBUG retrieval error:", e, file=sys.stdout)
        items = []; posts = []

    # randomly pick up to 3 items if many matches, then include address and telephone in snippets
    if items and len(items) > 3:
        try:
            items = random.sample(items, 3)
        except Exception:
            items = items[:3]
    item_snips = [f"{i.title} — {i.addr1 or ''} " for i in items]
    post_snips = [f"{p.title}: {(p.content or '')[:200]}" for p in posts]
    context_text = ""
    if items: context_text += "Items:\n" + "\n".join(item_snips) + "\n\n"
    if posts: context_text += "Posts:\n" + "\n".join(post_snips) + "\n\n"
    print("DEBUG context_text length:", len(context_text), file=sys.stdout)

    # If DB retrieval returned any results, prefer using them as context for the LLM (RAG)
    if items or posts:
        # Build context for LLM
        context_parts = []
        if items:
            context_parts.append("Items:")
            context_parts.extend(item_snips[:12])
        if posts:
            context_parts.append("Posts:")
            context_parts.extend(post_snips[:12])
        context_text = "\n".join(context_parts)

        # If OpenAI available, ask model to answer using the provided context first
        if openai.api_key:
            system_msg = (
                "You are a helpful Korean local assistant. Use the provided Context to answer the user's question. "
                "Be concise and conversational (like a chat reply). If the Context contains relevant items or posts, cite them briefly. "
                "Do NOT invent facts beyond the provided Context unless the user asks for general suggestions. "
                "Always output a short final answer in Korean."
            )
            user_prompt = f"User query: {q}\nRegion hint: {region_guess or region}\nContext:\n{context_text}\n\nAnswer concisely in Korean, referencing context when relevant."
            try:
                client = openai.OpenAI()
                resp = client.chat.completions.create(
                    model="gpt-5-mini",
                    messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_prompt}],
                    max_completion_tokens=300,
                )
                extracted = ""
                try:
                    if getattr(resp, "choices", None):
                        extracted = getattr(resp.choices[0].message, "content", "") or ""
                except Exception:
                    extracted = ""
                if not extracted:
                    try:
                        extracted = (resp["choices"][0]["message"]["content"] or "").strip()
                    except Exception:
                        extracted = ""
                if extracted:
                    reply = extracted.strip()
                    print("DEBUG openai RAG reply length:", len(reply), file=sys.stdout)
                    return {"reply": reply, "items": item_snips, "posts": post_snips, "intent": intent}
                else:
                    print("DEBUG openai RAG returned empty, falling back to DB summary", file=sys.stdout)
            except Exception as e:
                print("DEBUG OpenAI RAG call error:", e, file=sys.stdout)

        # If OpenAI not available or returned empty, return DB summary as fallback
        if items and posts:
            reply_parts = ["검색된 장소:"]
            reply_parts.extend(item_snips[:6])
            reply_parts.append("\n관련 게시글:")
            reply_parts.extend(post_snips[:6])
            reply = "\n".join(reply_parts)
        elif items:
            if category_token:
                reply = f"다음은 '{category_token}' 관련 추천 장소입니다:\n" + "\n".join(item_snips[:6])
            else:
                reply = "다음 장소를 찾았습니다:\n" + "\n".join(item_snips[:6])
        else:
            reply = "관련 게시글을 찾았습니다:\n" + "\n".join(post_snips[:6])
        print("DEBUG reply (DB fallback)", file=sys.stdout)
        return {"reply": reply, "items": item_snips, "posts": post_snips, "intent": intent}

    # If no DB results and no posts, do NOT call external LLM or return canned defaults.
    if not items and not posts:
        reply = "해당 조건에 맞는 데이터가 없습니다."
        print("DEBUG no DB data; returning no-data reply", file=sys.stdout)
        return {"reply": reply, "items": item_snips, "posts": post_snips, "intent": intent}
    print("DEBUG final reply length:", len(reply), file=sys.stdout)

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