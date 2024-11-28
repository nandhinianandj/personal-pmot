from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Story(Base):
    __tablename__ = "stories"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    takeoff = Column(String)
    turbulence = Column(String)
    touchdown = Column(String)
    media_links = relationship("MediaLink", back_populates="story", cascade="all, delete-orphan")

class MediaLink(Base):
    __tablename__ = "media_links"
    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id"))
    media_type = Column(String)
    url = Column(String)
    story = relationship("Story", back_populates="media_links")
