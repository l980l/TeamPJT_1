from datetime import datetime
from pydantic import BaseModel
from typing import Optional

# 기존 Item 스키마들은 그대로 둠

class PostBase(BaseModel):
    title: str
    content: str
    author: Optional[str] = None
    is_anonymous: Optional[bool] = True
    category: Optional[str] = None

class PostCreate(PostBase):
    edit_password: Optional[str] = None

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None
    is_anonymous: Optional[bool] = None
    category: Optional[str] = None
    edit_password: Optional[str] = None

class PostOut(PostBase):
    id: int
    views: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True