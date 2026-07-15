from typing import Optional
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi import Body
from pydantic import BaseModel
from . import models, schemas, crud
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="LocalHub API")

# 기존 /items 엔드포인트는 그대로
@app.get("/items", response_model=list[schemas.ItemOut])
def read_items(skip: int = 0, limit: int = 100, q: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Item)
    if q:
        query = query.filter(models.Item.title.contains(q))
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