from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, Text, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Item(Base):
    __tablename__ = "items"

    contentid = Column(String, primary_key=True, index=True)
    contenttypeid = Column(String, index=True)
    title = Column(String, index=True)
    addr1 = Column(String, nullable=True)
    addr2 = Column(String, nullable=True)
    zipcode = Column(String, nullable=True)
    tel = Column(String, nullable=True)
    mapx = Column(Float, nullable=True)
    mapy = Column(Float, nullable=True)
    mlevel = Column(String, nullable=True)
    areacode = Column(String, nullable=True)
    sigungucode = Column(String, nullable=True)
    lDongRegnCd = Column(String, nullable=True)
    lDongSignguCd = Column(String, nullable=True)
    cat1 = Column(String, nullable=True)
    cat2 = Column(String, nullable=True)
    cat3 = Column(String, nullable=True)
    lclsSystm1 = Column(String, nullable=True)
    lclsSystm2 = Column(String, nullable=True)
    lclsSystm3 = Column(String, nullable=True)
    firstimage = Column(String, nullable=True)
    firstimage2 = Column(String, nullable=True)
    cpyrhtDivCd = Column(String, nullable=True)
    createdtime = Column(String, nullable=True)
    modifiedtime = Column(String, nullable=True)
    region = Column(String, nullable=True)
    contentType = Column(String, nullable=True)


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False, index=True)
    content = Column(Text, nullable=False)
    author = Column(String, nullable=True)
    is_anonymous = Column(Boolean, nullable=False, default=True)
    views = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, server_default=func.datetime('now'))
    updated_at = Column(DateTime, nullable=False, server_default=func.datetime('now'), onupdate=func.datetime('now'))
    category = Column(String, nullable=True, index=True)
    place_contentid = Column(String, nullable=True)
    place_title = Column(String, nullable=True)
    place_addr = Column(String, nullable=True)
    edit_password = Column(String, nullable=True)   
    likes = Column(Integer, nullable=False, default=0)   
