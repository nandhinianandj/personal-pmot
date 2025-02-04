import pytest
import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..database import Base

@pytest.fixture(scope="session")
def temp_db_path():
    fd, path = tempfile.mkstemp()
    yield path
    os.close(fd)
    os.unlink(path)

@pytest.fixture(scope="session")
def db_engine(temp_db_path):
    engine = create_engine(f"sqlite:///{temp_db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(db_engine):
    Session = sessionmaker(bind=db_engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()