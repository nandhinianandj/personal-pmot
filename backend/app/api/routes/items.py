import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import PMOT, PMOTCreate, PMOTPublic, PMOTsPublic, PMOTUpdate, Message

router = APIRouter()


@router.get("/", response_model=PMOTsPublic)
def read_items(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve items.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(PMOT)
        count = session.exec(count_statement).one()
        statement = select(PMOT).offset(skip).limit(limit)
        items = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(PMOT)
            .where(PMOT.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(PMOT)
            .where(PMOT.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        items = session.exec(statement).all()

    return PMOTsPublic(data=items, count=count)


@router.get("/{id}", response_model=PMOTPublic)
def read_item(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get item by ID.
    """
    item = session.get(PMOT, id)
    if not item:
        raise HTTPException(status_code=404, detail="PMOT not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return item


@router.post("/", response_model=PMOTPublic)
def create_item(
    *, session: SessionDep, current_user: CurrentUser, item_in: PMOTCreate
) -> Any:
    """
    Create new item.
    """
    item = PMOT.model_validate(item_in, update={"owner_id": current_user.id})
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.put("/{id}", response_model=PMOTPublic)
def update_item(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    item_in: PMOTUpdate,
) -> Any:
    """
    Update an item.
    """
    item = session.get(PMOT, id)
    if not item:
        raise HTTPException(status_code=404, detail="PMOT not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = item_in.model_dump(exclude_unset=True)
    item.sqlmodel_update(update_dict)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.delete("/{id}")
def delete_item(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an item.
    """
    item = session.get(PMOT, id)
    if not item:
        raise HTTPException(status_code=404, detail="PMOT not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(item)
    session.commit()
    return Message(message="PMOT deleted successfully")
