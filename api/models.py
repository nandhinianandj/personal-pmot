from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    private_key = Column(String, nullable=True)
    public_key = Column(String, nullable=True)
    actor_url = Column(String, unique=True, nullable=True)
    inbox_url = Column(String, unique=True, nullable=True)
    outbox_url = Column(String, unique=True, nullable=True)
    followers_url = Column(String, unique=True, nullable=True)
    following_url = Column(String, unique=True, nullable=True)
    stories = relationship("Story", back_populates="author")
    followers = relationship("Follow", foreign_keys="Follow.following_id", back_populates="following")
    following = relationship("Follow", foreign_keys="Follow.follower_id", back_populates="follower")

class Story(Base):
    __tablename__ = "stories"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    takeoff = Column(String)
    turbulence = Column(String)
    touchdown = Column(String)
    author_id = Column(Integer, ForeignKey("users.id"))
    remote_id = Column(String, unique=True, nullable=True)
    remote_author = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author = relationship("User", back_populates="stories")
    media_links = relationship("MediaLink", back_populates="story", cascade="all, delete-orphan")

class MediaLink(Base):
    __tablename__ = "media_links"
    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id"))
    media_type = Column(String)
    url = Column(String)
    story = relationship("Story", back_populates="media_links")

class Follow(Base):
    __tablename__ = "follows"
    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id"))
    following_id = Column(Integer, ForeignKey("users.id"))
    remote_actor = Column(String, nullable=True)
    accepted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    follower = relationship("User", foreign_keys=[follower_id], back_populates="following")
    following = relationship("User", foreign_keys=[following_id], back_populates="followers")