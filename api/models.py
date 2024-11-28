from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
# local imports
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_premium = Column(Boolean, default=False)
    stories = relationship("Story", back_populates="author")
    subscriptions = relationship("Subscription", back_populates="user")

class Story(Base):
    __tablename__ = "stories"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    takeoff = Column(String)
    turbulence = Column(String)
    touchdown = Column(String)
    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="stories")
    media_links = relationship("MediaLink", back_populates="story", cascade="all, delete-orphan")

class MediaLink(Base):
    __tablename__ = "media_links"
    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id"))
    media_type = Column(String)
    url = Column(String)
    story = relationship("Story", back_populates="media_links")

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    plan_id = Column(String)
    status = Column(String)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    amount = Column(Float)
    payment_id = Column(String, unique=True)
    user = relationship("User", back_populates="subscriptions")

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)
    payment_id = Column(String, unique=True)
    order_id = Column(String, unique=True)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
