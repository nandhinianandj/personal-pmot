from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MediaLinkBase(BaseModel):
    media_type: str
    url: str

class MediaLinkCreate(MediaLinkBase):
    pass

class MediaLink(MediaLinkBase):
    id: int
    story_id: int

    class Config:
        from_attributes = True

class StoryBase(BaseModel):
    title: str
    takeoff: str
    turbulence: str
    touchdown: str

class StoryCreate(StoryBase):
    media_links: List[MediaLinkCreate] = []

class Story(StoryBase):
    id: int
    author_id: int
    remote_id: Optional[str] = None
    remote_author: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    media_links: List[MediaLink] = []

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: str
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    actor_url: Optional[str] = None
    inbox_url: Optional[str] = None
    outbox_url: Optional[str] = None
    followers_url: Optional[str] = None
    following_url: Optional[str] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class FollowCreate(BaseModel):
    remote_actor: str

class Follow(BaseModel):
    id: int
    follower_id: int
    following_id: Optional[int] = None
    remote_actor: Optional[str] = None
    accepted: bool
    created_at: datetime

    class Config:
        from_attributes = True