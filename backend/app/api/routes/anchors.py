import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import Anchor, AnchorCreate, AnchorPublic, Message

router = APIRouter()


@router.post("/", response_model=AnchorPublic)
def create_anchor(
    *, session: SessionDep, current_user: CurrentUser, anchor_in: AnchorCreate
) -> Any:
    """
    Create new anchor.
    """
    anchor = crud.create_anchor(session=session, anchor_in=anchor_in)
    return anchor
