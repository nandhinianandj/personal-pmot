from typing import List
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import os
import shutil
from pathlib import Path

# local imports
import models, schemas, auth
from database import SessionLocal, engine
from payments import PaymentGateway
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
payment_gateway = PaymentGateway()

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

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(auth.get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: Session = Depends(auth.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/premium/order")
async def create_premium_order(
    current_user: models.User = Depends(auth.get_current_user)
):
    amount = 999.0  # ₹999 for premium subscription
    order = payment_gateway.create_order(amount)
    return order

@app.post("/premium/verify")
async def verify_premium_payment(
    payment: schemas.PaymentVerification,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if payment_gateway.verify_payment(
        payment.payment_id,
        payment.order_id,
        payment.signature
    ):
        current_user.is_premium = True
        db.add(current_user)
        db.commit()
        return {"status": "success"}
    raise HTTPException(status_code=400, detail="Payment verification failed")

@app.post("/stories/", response_model=schemas.Story)
async def create_story(
    story: schemas.StoryCreate,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if not current_user.is_premium and len(current_user.stories) >= 3:
        raise HTTPException(
            status_code=403,
            detail="Free users can only create up to 3 stories. Upgrade to premium for unlimited stories."
        )
    
    db_story = models.Story(
        title=story.title,
        takeoff=story.takeoff,
        turbulence=story.turbulence,
        touchdown=story.touchdown,
        author_id=current_user.id
    )
    db.add(db_story)
    db.commit()
    db.refresh(db_story)
    
    for media_link in story.media_links:
        db_media = models.MediaLink(
            story_id=db_story.id,
            media_type=media_link.media_type,
            url=media_link.url
        )
        db.add(db_media)
    
    db.commit()
    db.refresh(db_story)
    return db_story

@app.get("/stories/", response_model=List[schemas.Story])
async def read_stories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    stories = db.query(models.Story).filter(
        models.Story.author_id == current_user.id
    ).offset(skip).limit(limit).all()
    return stories

@app.get("/stories/{story_id}", response_model=schemas.Story)
async def read_story(
    story_id: int,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    story = db.query(models.Story).filter(
        models.Story.id == story_id,
        models.Story.author_id == current_user.id
    ).first()
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    return story

@app.put("/stories/{story_id}", response_model=schemas.Story)
async def update_story(
    story_id: int,
    story: schemas.StoryCreate,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_story = db.query(models.Story).filter(
        models.Story.id == story_id,
        models.Story.author_id == current_user.id
    ).first()
    if db_story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    
    for key, value in story.dict(exclude={'media_links'}).items():
        setattr(db_story, key, value)
    
    db.query(models.MediaLink).filter(models.MediaLink.story_id == story_id).delete()
    for media_link in story.media_links:
        db_media = models.MediaLink(
            story_id=story_id,
            media_type=media_link.media_type,
            url=media_link.url
        )
        db.add(db_media)
    
    db.commit()
    db.refresh(db_story)
    return db_story

@app.delete("/stories/{story_id}")
async def delete_story(
    story_id: int,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    story = db.query(models.Story).filter(
        models.Story.id == story_id,
        models.Story.author_id == current_user.id
    ).first()
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    db.delete(story)
    db.commit()
    return {"message": "Story deleted"}
