import uuid

from pydantic import EmailStr
from sqlmodel import Field, Enum, Relationship, SQLModel
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


import enum
from datetime import date

from sqlmodel import Column, Enum


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    pmots: list["PMOT"] = Relationship(back_populates="owner", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


class EmotionImpact(str, enum.Enum):
    xtreme_sad = "Extremely Sad"
    sad = "Sad"
    meh = "Ambivalent"
    happy = "Happy"
    xtreme_happy = "Extremely Happy"


class AnchorType(str, enum.Enum):
    text = "text"
    image = "image"
    audio = "audio"
    video = "video"
    file = "file"


class StoryArc(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=255)


class EmpathyMatrix(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=255)


class PMOTDetailsStrengthLink(SQLModel, table=True):
    pmot_details_id: uuid.UUID | None = Field(
        default=None, foreign_key="pmotdetails.id", primary_key=True
    )
    strength_id: uuid.UUID | None = Field(
        default=None, foreign_key="strength.id", primary_key=True
    )


class Strength(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=255)
    pmot_details: list["PMOTDetails"] = Relationship(
        back_populates="strengths", link_model=PMOTDetailsStrengthLink
    )


class PMOTBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    event_date: date = Field(default_factory=date.today, nullable=False)
    short_story: str = Field(min_length=1, max_length=5500)
    emotional_impact: EmotionImpact | None = Field(
        default=None, sa_column=Column(Enum(EmotionImpact))
    )


class PMOTCreate(PMOTBase):
    pass


class PMOTUpdate(PMOTBase):
    pass


class AnchorBase(SQLModel):
    anchor_type: AnchorType = Field(sa_column=Column(Enum(AnchorType)))
    content: str


class AnchorCreate(AnchorBase):
    pass


class AnchorPublic(AnchorBase):
    id: uuid.UUID


class Anchor(AnchorBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    pmot_details_id: uuid.UUID = Field(foreign_key="pmotdetails.id")
    pmot_details: "PMOTDetails" = Relationship(back_populates="anchors")


class PMOT(PMOTBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    owner: User = Relationship(back_populates="pmots")
    details: "PMOTDetails" = Relationship(
        back_populates="pmot", sa_relationship_kwargs={"uselist": False}
    )


class PMOTDetails(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    pmot_id: uuid.UUID = Field(foreign_key="pmot.id")
    pmot: PMOT = Relationship(back_populates="details")
    det_story: str | None = Field(default=None, min_length=1, max_length=5500)
    story_arc_id: uuid.UUID | None = Field(default=None, foreign_key="storyarc.id")
    story_arc: StoryArc | None = Relationship()
    empathy_matrix_id: uuid.UUID | None = Field(
        default=None, foreign_key="empathymatrix.id"
    )
    empathy_matrix: EmpathyMatrix | None = Relationship()
    strengths: list[Strength] = Relationship(
        back_populates="pmot_details", link_model=PMOTDetailsStrengthLink
    )
    anchors: list[Anchor] = Relationship(back_populates="pmot_details")


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
