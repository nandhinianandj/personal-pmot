from typing import List
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os
import shutil
from pathlib import Path

from database import SessionLocal, engine
import models, schemas

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Mount the uploads directory
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_path = UPLOAD_DIR / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"url": f"/uploads/{file.filename}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/stories/", response_model=schemas.Story)
def create_story(story: schemas.StoryCreate, db: Session = Depends(get_db)):
    db_story = models.Story(
        title=story.title,
        takeoff=story.takeoff,
        turbulence=story.turbulence,
        touchdown=story.touchdown
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
def read_stories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    stories = db.query(models.Story).offset(skip).limit(limit).all()
    return stories

@app.get("/stories/{story_id}", response_model=schemas.Story)
def read_story(story_id: int, db: Session = Depends(get_db)):
    story = db.query(models.Story).filter(models.Story.id == story_id).first()
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    return story

@app.put("/stories/{story_id}", response_model=schemas.Story)
def update_story(story_id: int, story: schemas.StoryCreate, db: Session = Depends(get_db)):
    db_story = db.query(models.Story).filter(models.Story.id == story_id).first()
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
def delete_story(story_id: int, db: Session = Depends(get_db)):
    story = db.query(models.Story).filter(models.Story.id == story_id).first()
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    db.delete(story)
    db.commit()
    return {"message": "Story deleted"}
