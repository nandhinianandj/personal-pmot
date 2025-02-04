import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..database import Base
from ..main import app, get_db
from .. import models

# Use SQLite in-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=engine)
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.fixture
def test_user(test_db):
    user = models.User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password",
        actor_url="https://test.example.com/users/testuser",
        inbox_url="https://test.example.com/users/testuser/inbox",
        outbox_url="https://test.example.com/users/testuser/outbox",
        followers_url="https://test.example.com/users/testuser/followers",
        following_url="https://test.example.com/users/testuser/following"
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

def test_get_user_actor(client, test_user):
    response = client.get(f"/users/{test_user.username}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["type"] == "Person"
    assert data["id"] == test_user.actor_url
    assert data["inbox"] == test_user.inbox_url
    assert data["outbox"] == test_user.outbox_url
    assert data["followers"] == test_user.followers_url
    assert data["following"] == test_user.following_url
    assert "publicKey" in data

def test_get_nonexistent_user_actor(client):
    response = client.get("/users/nonexistent")
    assert response.status_code == 404

def test_post_to_inbox_create_story(client, test_user):
    activity = {
        "type": "Create",
        "actor": "https://remote.example.com/users/remote_user",
        "object": {
            "type": "Article",
            "id": "https://remote.example.com/stories/123",
            "content": '{"title": "Remote Story", "takeoff": "Remote takeoff", "turbulence": "Remote turbulence", "touchdown": "Remote touchdown"}'
        }
    }
    
    response = client.post(f"/users/{test_user.username}/inbox", json=activity)
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"

def test_post_to_inbox_follow(client, test_user):
    activity = {
        "type": "Follow",
        "actor": "https://remote.example.com/users/follower",
        "object": f"https://test.example.com/users/{test_user.username}"
    }
    
    response = client.post(f"/users/{test_user.username}/inbox", json=activity)
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"

def test_get_user_outbox(client, test_user, test_db):
    # Create a test story
    story = models.Story(
        title="Test Story",
        takeoff="Test takeoff",
        turbulence="Test turbulence",
        touchdown="Test touchdown",
        author_id=test_user.id
    )
    test_db.add(story)
    test_db.commit()
    
    response = client.get(f"/users/{test_user.username}/outbox")
    assert response.status_code == 200
    
    data = response.json()
    assert data["type"] == "OrderedCollection"
    assert data["totalItems"] == 1
    
    activity = data["orderedItems"][0]
    assert activity["type"] == "Create"
    assert activity["actor"] == test_user.actor_url
    
    obj = activity["object"]
    assert obj["type"] == "Article"
    assert "content" in obj