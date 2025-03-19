from fastapi.testclient import TestClient
from main import app, get_db
from database import Base, engine, SessionLocal
from sqlalchemy.orm import sessionmaker
import pytest

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_create_note():
    response = client.post("/notes/", json={"title": "Test Note", "content": "This is a test content"})
    assert response.status_code == 200
    assert response.json()["title"] == "Test Note"


def test_get_note():
    response = client.post("/notes/", json={"title": "Sample", "content": "Content"})
    note_id = response.json()["id"]

    response = client.get(f"/notes/{note_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Sample"


def test_update_note():
    response = client.post("/notes/", json={"title": "Old Title", "content": "Old Content"})
    note_id = response.json()["id"]

    update_response = client.put(f"/notes/{note_id}", json={"title": "New Title", "content": "New Content"})
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "New Title"


def test_delete_note():
    response = client.post("/notes/", json={"title": "To Delete", "content": "Will be deleted"})
    note_id = response.json()["id"]

    delete_response = client.delete(f"/notes/{note_id}")
    assert delete_response.status_code == 200

    get_response = client.get(f"/notes/{note_id}")
    assert get_response.status_code == 404


def test_summarize_note(mocker):
    response = client.post("/notes/", json={"title": "Summary Test", "content": "This is a long note that should be summarized."})
    note_id = response.json()["id"]

    mocker.patch("ai_utils.summarize_note", return_value="Short summary.")
    summary_response = client.get(f"/notes/{note_id}/summarize/")
    assert summary_response.status_code == 200
    assert summary_response.json()["summary"] == "Short summary."


def test_analytics():
    client.post("/notes/", json={"title": "Note 1", "content": "This is the first note"})
    client.post("/notes/", json={"title": "Note 2", "content": "Second note with more text"})
    client.post("/notes/", json={"title": "Note 3", "content": "Short"})

    analytics_response = client.get("/analytics/")
    assert analytics_response.status_code == 200
    data = analytics_response.json()
    assert data["total_notes"] == 3
    assert "total_words" in data
    assert "average_length" in data
    assert "most_common_words" in data


def test_get_non_existent_note():
    response = client.get("/notes/9999")
    assert response.status_code == 404


def test_delete_non_existent_note():
    response = client.delete("/notes/9999")
    assert response.status_code == 200
    assert response.json()["message"] == "Note not found"


def test_update_non_existent_note():
    response = client.put("/notes/9999", json={"title": "Updated", "content": "New Content"})
    assert response.status_code == 200
    assert response.json() is None
