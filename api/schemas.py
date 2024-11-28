from pydantic import BaseModel
from typing import List, Optional

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
    media_links: List[MediaLink] = []

    class Config:
        from_attributes = True