from sqlmodel import Session

from app import crud
from app.models import PMOT, PMOTCreate
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def create_random_pmot(db: Session) -> PMOT:
    user = create_random_user(db)
    owner_id = user.id
    assert owner_id is not None
    title = random_lower_string()
    description = random_lower_string()
    short_story = random_lower_string()
    pmot_in = PMOTCreate(
        title=title, description=description, short_story=short_story
    )
    return crud.create_pmot(session=db, pmot_in=pmot_in, owner_id=owner_id)
