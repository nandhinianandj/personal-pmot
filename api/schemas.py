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
    is_premium: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class PaymentVerification(BaseModel):
    payment_id: str
    order_id: str
    signature: str

class SubscriptionCreate(BaseModel):
    plan_id: str
    amount: float

class Subscription(SubscriptionCreate):
    id: int
    user_id: int
    status: str
    start_date: datetime
    end_date: datetime
    payment_id: str

    class Config:
        from_attributes = True