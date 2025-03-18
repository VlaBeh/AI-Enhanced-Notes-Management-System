from sqlalchemy.orm import Session
from models import Note
from schemas import NoteCreate, NoteUpdate


def create_note(db: Session, note: NoteCreate):
    db_note = Note(**note.dict())
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


def get_note_by_id(db: Session, note_id: int):
    return db.query(Note).filter(Note.id == note_id).first()


def update_note(db: Session, note_id: int, note: NoteUpdate):
    db_note = get_note_by_id(db, note_id)
    if not db_note:
        return None
    db_note.title = note.title
    db_note.content = note.content
    db.commit()
    db.refresh(db_note)
    return db_note


def delete_note(db: Session, note_id: int):
    db_note = get_note_by_id(db, note_id)
    if db_note:
        db.delete(db_note)
        db.commit()
        return {"message": "Note deleted"}
    return {"message": "Note not found"}
