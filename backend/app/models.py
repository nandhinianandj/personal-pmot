import uuid

from enum import Enum as pyEnum
from pydantic import EmailStr
from sqlmodel import Field, Enum , Relationship, SQLModel, Column
from datetime import datetime


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["PMOT"] = Relationship(back_populates="owner", 
                                       cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class EmotionImpact(str, Enum):
    xtreme_sad = "Extremely Sad"
    sad = "Sad"
    meh = "Ambivalent"
    happy = "Happy"
    xtreme_happy = "Extremely Happy"

class PMOTBase(SQLModel):
    label: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    event_date: datetime = Field(default_factory=datetime.utcnow,nullable=False)
    short_story: str = Field(min_length=1, max_length=5500)
    #emotional_impact: EmotionImpact = Field(Column(Enum(EmotionImpact)))
    show_on_jl: bool = False

class Anchor(SQLModel):
    pass

class StoryArc(SQLModel):
    pass

# Properties to receive on item creation
class PMOTCreate(PMOTBase):
    created_at: datetime = Field(default_factory=datetime.utcnow,nullable=False)


# Properties to receive on item update
class PMOTUpdate(PMOTBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore
    updated_at: datetime = Field(default_factory=datetime.utcnow,nullable=False)


# Database model, database table inferred from class name
class PMOT(PMOTBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")

class PMOTDetails(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    pmot_id: uuid.UUID = Field(foreign_key="PMOT.id", nullable=False, ondelete="RESTRICT")
    det_story: str = Field(min_length=1, max_length=5500)
    #story_arc: StoryArc = Relationship(back_populates="StoryArc", 
                                          #cascade_delete=False)
    #anchors : list[Anchor] = Relationship(back_populates="Anchor", 
    #                                      cascade_delete=False)
    #empathy_matrix: EmpathyMatrix = empathy_mat_obj
    #strengths1: list[Strength] = list_of_strength_objs

class PMOTDetailsUpdate(PMOTBase):
    updated_at: datetime = Field(default_factory=datetime.utcnow,nullable=False)

# Properties to return via API, id is always required
class PMOTPublic(PMOTBase):
    id: uuid.UUID
    owner_id: uuid.UUID

class PMOTsPublic(SQLModel):
    data: list[PMOTPublic]
    count: int

# Generic message
class Message(SQLModel):
    message: str

# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)
