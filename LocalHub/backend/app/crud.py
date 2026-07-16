from datetime import datetime
from sqlalchemy.orm import Session
from . import models, schemas

# 기존 Item 관련 함수는 그대로 둠

def increment_views(db: Session, post_id: int):
    db_post = get_post(db, post_id)
    if not db_post: return None
    db_post.views = (db_post.views or 0) + 1
    db.add(db_post); db.commit(); db.refresh(db_post)
    return db_post

def like_post(db: Session, post_id: int):
    db_post = get_post(db, post_id)
    if not db_post: return None
    db_post.likes = (db_post.likes or 0) + 1
    db.add(db_post); db.commit(); db.refresh(db_post)
    return db_post

def get_posts(db: Session, skip: int = 0, limit: int = 100, q: str | None = None, category: str | None = None):
    query = db.query(models.Post)
    if q:
        query = query.filter((models.Post.title.contains(q)) | (models.Post.content.contains(q)))
    if category:
        query = query.filter(models.Post.category == category)
    return query.offset(skip).limit(limit).all()

def get_post(db: Session, post_id: int):
    return db.query(models.Post).filter(models.Post.id == post_id).first()

def create_post(db: Session, post: schemas.PostCreate):
    db_post = models.Post(
        title=post.title,
        content=post.content,
        author=post.author,
        is_anonymous=post.is_anonymous,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        category=post.category,
        place_contentid=getattr(post, "place_contentid", None),
        place_title=getattr(post, "place_title", None),
        place_addr=getattr(post, "place_addr", None),
        edit_password=post.edit_password,
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def update_post(db: Session, post_id: int, post: schemas.PostUpdate, password: str | None = None):
    db_post = get_post(db, post_id)
    if not db_post:
        return None
    if db_post.edit_password:
        if password is None or password != db_post.edit_password:
            raise PermissionError("Password mismatch")
    else:
        # if no password was set at creation, deny modification (or choose policy)
        raise PermissionError("No password set for this post")
    for key, value in post.dict(exclude_unset=True).items():
        setattr(db_post, key, value)
    db_post.updated_at = datetime.utcnow()
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def delete_post(db: Session, post_id: int, password: str | None = None):
    db_post = get_post(db, post_id)
    if not db_post:
        return False
    if db_post.edit_password:
        if password is None or password != db_post.edit_password:
            raise PermissionError("Password mismatch")
    else:
        raise PermissionError("No password set for this post")
    db.delete(db_post)
    db.commit()
    return True

def increment_views(db: Session, post_id: int):
    db_post = get_post(db, post_id)
    if not db_post: return None
    db_post.views = (db_post.views or 0) + 1
    db.add(db_post); db.commit(); db.refresh(db_post)
    return db_post

def like_post(db: Session, post_id: int):
    db_post = get_post(db, post_id)
    if not db_post: return None
    db_post.likes = (db_post.likes or 0) + 1
    db.add(db_post); db.commit(); db.refresh(db_post)
    return db_post

def search_items(db: Session, q: str | None = None, region: str | None = None, category: str | None = None, limit: int = 6):
    query = db.query(models.Item)
    if q:
        query = query.filter(models.Item.title.contains(q))
    if region:
        query = query.filter((models.Item.region == region) | (models.Item.addr1.contains(region)))
    if category:
        # use contains to be tolerant of variations (e.g. '쇼핑', '숙박', '여행코스')
        query = query.filter(models.Item.contentType.contains(category))
    return query.limit(limit).all()

def search_posts(db: Session, q: str | None = None, category: str | None = None, limit: int = 5):
    query = db.query(models.Post)
    if q:
        query = query.filter((models.Post.title.contains(q)) | (models.Post.content.contains(q)))
    if category:
        query = query.filter(models.Post.category == category)
    return query.order_by(models.Post.created_at.desc()).limit(limit).all()