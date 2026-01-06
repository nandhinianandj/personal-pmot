import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import Message, PMOT, PMOTCreate, PMOTPublic, PMOTsPublic, PMOTUpdate

router = APIRouter()


@router.get("/", response_model=PMOTsPublic)
def read_pmots(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve pmots.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(PMOT)
        count = session.exec(count_statement).one()
        statement = select(PMOT).offset(skip).limit(limit)
        pmots = session.exec(statement).all()
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
        pmots = session.exec(statement).all()

    return PMOTsPublic(data=pmots, count=count)


@router.get("/{id}", response_model=PMOTPublic)
def read_pmot(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get pmot by ID.
    """
    pmot = session.get(PMOT, id)
    if not pmot:
        raise HTTPException(status_code=404, detail="PMOT not found")
    if not current_user.is_superuser and (pmot.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return pmot


@router.post("/", response_model=PMOTPublic)
def create_pmot(
    *, session: SessionDep, current_user: CurrentUser, pmot_in: PMOTCreate
) -> Any:
    """
    Create new pmot.
    """
    pmot = crud.create_pmot(session=session, pmot_in=pmot_in, owner_id=current_user.id)
    return pmot


@router.put("/{id}", response_model=PMOTPublic)
def update_pmot(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    pmot_in: PMOTUpdate,
) -> Any:
    """
    Update a pmot.
    """
    pmot = session.get(PMOT, id)
    if not pmot:
        raise HTTPException(status_code=404, detail="PMOT not found")
    if not current_user.is_superuser and (pmot.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = pmot_in.model_dump(exclude_unset=True)
    pmot.sqlmodel_update(update_dict)
    session.add(pmot)
    session.commit()
    session.refresh(pmot)
    return pmot


@router.delete("/{id}")
def delete_pmot(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete a pmot.
    """
    pmot = session.get(PMOT, id)
    if not pmot:
        raise HTTPException(status_code=404, detail="PMOT not found")
    if not current_user.is_superuser and (pmot.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(pmot)
    session.commit()
    return Message(message="PMOT deleted successfully")
