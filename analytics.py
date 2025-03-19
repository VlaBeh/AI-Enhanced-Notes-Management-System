from sqlalchemy.orm import Session
from models import Note
import pandas as pd
import nltk
from collections import Counter

nltk.download("punkt")


def analyze_notes(db: Session):
    notes = db.query(Note).all()
    texts = [note.content for note in notes]
    words = [word for text in texts for word in nltk.word_tokenize(text)]

    total_words = len(words)
    avg_length = total_words / len(notes) if notes else 0
    common_words = Counter(words).most_common(10)

    note_lengths = sorted([(note.id, len(nltk.word_tokenize(note.content))) for note in notes], key=lambda x: x[1])

    return {
        "total_notes": len(notes),
        "total_words": total_words,
        "average_length": avg_length,
        "most_common_words": common_words,
        "longest_notes": note_lengths[-3:],
        "shortest_notes": note_lengths[:3],
    }
