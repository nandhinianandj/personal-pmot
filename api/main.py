from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from . import models, schemas, auth
from .database import SessionLocal, engine
from .activitypub import ActivityPubProtocol
import os
import json
from pathlib import Path

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
activitypub = ActivityPubProtocol(os.getenv("DOMAIN", "localhost:8000"))

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ActivityPub Endpoints
@app.get("/users/{username}")
async def get_user_actor(username: str, db: Session = Depends(auth.get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Person",
        "id": user.actor_url,
        "inbox": user.inbox_url,
        "outbox": user.outbox_url,
        "followers": user.followers_url,
        "following": user.following_url,
        "publicKey": {
            "id": f"{user.actor_url}#main-key",
            "owner": user.actor_url,
            "publicKeyPem": user.public_key
        }
    }

@app.post("/users/{username}/inbox")
async def user_inbox(username: str, request: Request, db: Session = Depends(auth.get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    activity = await request.json()
    processed = activitypub.process_incoming_activity(activity)
    
    if processed["type"] == "Story":
        story = models.Story(
            title=processed["title"],
            takeoff=processed["takeoff"],
            turbulence=processed["turbulence"],
            touchdown=processed["touchdown"],
            remote_id=processed["remote_id"],
            remote_author=processed["remote_author"],
            author_id=user.id
        )
        db.add(story)
        db.commit()
    elif processed["type"] == "Follow":
        follow = models.Follow(
            follower_id=user.id,
            remote_actor=processed["follower"]
        )
        db.add(follow)
        db.commit()
    
    return {"status": "accepted"}

@app.get("/users/{username}/outbox")
async def user_outbox(username: str, db: Session = Depends(auth.get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    stories = db.query(models.Story).filter(models.Story.author_id == user.id).all()
    activities = []
    
    for story in stories:
        activity = activitypub.create_story_activity(
            {
                "id": story.id,
                "title": story.title,
                "takeoff": story.takeoff,
                "turbulence": story.turbulence,
                "touchdown": story.touchdown
            },
            {"username": user.username}
        )
        activities.append(activity)
    
    return {
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "OrderedCollection",
        "totalItems": len(activities),
        "orderedItems": activities
    }

# Existing endpoints...
# (Keep all the existing endpoints from the previous main.py)