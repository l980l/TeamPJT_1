from datetime import datetime
from pydantic import BaseModel
from typing import Optional

# 기존 Item 스키마들은 그대로 둠
class ItemBase(BaseModel):
    contentid: str
    contenttypeid: Optional[str] = None
    title: Optional[str] = None
    addr1: Optional[str] = None
    addr2: Optional[str] = None
    zipcode: Optional[str] = None
    tel: Optional[str] = None
    mapx: Optional[float] = None
    mapy: Optional[float] = None
    firstimage: Optional[str] = None
    region: Optional[str] = None
    contentType: Optional[str] = None

class ItemOut(ItemBase):
    class Config:
        orm_mode = True
        
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
    likes: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
class PasswordBody(BaseModel):
    password: str