from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
from models import Note
from schemas import NoteCreate, NoteUpdate, NoteResponse
import crud
from ai_utils import summarize_note
from analytics import analyze_notes

Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/notes/", response_model=NoteResponse)
def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    return crud.create_note(db, note)


@app.get("/notes/{note_id}", response_model=NoteResponse)
def read_note(note_id: int, db: Session = Depends(get_db)):
    return crud.get_note_by_id(db, note_id)


@app.put("/notes/{note_id}", response_model=NoteResponse)
def update_note(note_id: int, note: NoteUpdate, db: Session = Depends(get_db)):
    return crud.update_note(db, note_id, note)


@app.delete("/notes/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    return crud.delete_note(db, note_id)


@app.get("/notes/{note_id}/summarize/")
def summarize(note_id: int, db: Session = Depends(get_db)):
    note = crud.get_note_by_id(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    summary = summarize_note(note.content)
    return {"summary": summary}


@app.get("/analytics/")
def get_analytics(db: Session = Depends(get_db)):
    return analyze_notes(db)
