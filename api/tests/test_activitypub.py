import pytest
from datetime import datetime
import json
from ..activitypub import ActivityPubProtocol
from fastapi import HTTPException
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from base64 import b64decode

@pytest.fixture
def activitypub():
    return ActivityPubProtocol("test.example.com")

@pytest.fixture
def sample_story():
    return {
        "id": 1,
        "title": "Test Story",
        "takeoff": "Test takeoff",
        "turbulence": "Test turbulence",
        "touchdown": "Test touchdown"
    }

@pytest.fixture
def sample_author():
    return {
        "username": "testuser"
    }

def test_initialization():
    ap = ActivityPubProtocol("test.example.com")
    assert ap.domain == "test.example.com"
    assert ap.private_key is not None

def test_public_key_generation(activitypub):
    public_key = activitypub.get_public_key_pem()
    assert "BEGIN PUBLIC KEY" in public_key
    assert "END PUBLIC KEY" in public_key

def test_message_signing_and_verification(activitypub):
    message = "Test message"
    signature = activitypub.sign_message(message)
    
    # Verify signature using public key
    public_key = activitypub.private_key.public_key()
    decoded_signature = b64decode(signature)
    
    try:
        public_key.verify(
            decoded_signature,
            message.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        verification_succeeded = True
    except Exception:
        verification_succeeded = False
    
    assert verification_succeeded

def test_create_story_activity(activitypub, sample_story, sample_author):
    activity = activitypub.create_story_activity(sample_story, sample_author)
    
    assert activity["@context"] == "https://www.w3.org/ns/activitystreams"
    assert activity["type"] == "Create"
    assert activity["actor"] == f"https://{activitypub.domain}/users/{sample_author['username']}"
    
    obj = activity["object"]
    assert obj["type"] == "Article"
    assert obj["id"] == f"https://{activitypub.domain}/stories/{sample_story['id']}"
    assert obj["attributedTo"] == activity["actor"]
    
    content = json.loads(obj["content"])
    assert content["title"] == sample_story["title"]
    assert content["takeoff"] == sample_story["takeoff"]
    assert content["turbulence"] == sample_story["turbulence"]
    assert content["touchdown"] == sample_story["touchdown"]

@pytest.mark.asyncio
async def test_deliver_to_inbox_invalid_url(activitypub, sample_story, sample_author):
    activity = activitypub.create_story_activity(sample_story, sample_author)
    
    with pytest.raises(HTTPException) as exc_info:
        await activitypub.deliver_to_inbox(activity, "https://invalid-url.example.com/inbox")
    
    assert exc_info.value.status_code == 502

def test_process_create_activity(activitypub):
    activity = {
        "type": "Create",
        "actor": "https://remote.example.com/users/remote_user",
        "object": {
            "type": "Article",
            "id": "https://remote.example.com/stories/123",
            "content": json.dumps({
                "title": "Remote Story",
                "takeoff": "Remote takeoff",
                "turbulence": "Remote turbulence",
                "touchdown": "Remote touchdown"
            })
        }
    }
    
    result = activitypub.process_incoming_activity(activity)
    
    assert result["type"] == "Story"
    assert result["title"] == "Remote Story"
    assert result["remote_id"] == "https://remote.example.com/stories/123"
    assert result["remote_author"] == "https://remote.example.com/users/remote_user"

def test_process_follow_activity(activitypub):
    activity = {
        "type": "Follow",
        "actor": "https://remote.example.com/users/follower",
        "object": "https://test.example.com/users/followed"
    }
    
    result = activitypub.process_incoming_activity(activity)
    
    assert result["type"] == "Follow"
    assert result["follower"] == "https://remote.example.com/users/follower"
    assert result["following"] == "https://test.example.com/users/followed"

def test_process_invalid_activity_type(activitypub):
    activity = {
        "type": "InvalidType",
        "actor": "https://remote.example.com/users/user",
        "object": {}
    }
    
    with pytest.raises(HTTPException) as exc_info:
        activitypub.process_incoming_activity(activity)
    
    assert exc_info.value.status_code == 400
    assert "Unsupported activity type" in exc_info.value.detail

def test_process_invalid_object_type(activitypub):
    activity = {
        "type": "Create",
        "actor": "https://remote.example.com/users/user",
        "object": {
            "type": "InvalidType",
            "content": "{}"
        }
    }
    
    with pytest.raises(HTTPException) as exc_info:
        activitypub.process_incoming_activity(activity)
    
    assert exc_info.value.status_code == 400
    assert "Unsupported object type" in exc_info.value.detail