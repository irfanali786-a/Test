# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_list_gists_default_user():
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    # If octocat has public gists, each item should have required keys
    if len(data) > 0:
        item = data[0]
        assert "id" in item
        assert "html_url" in item
        assert "files" in item
        assert "owner" in item
        assert isinstance(item["files"], list)

def test_list_gists_explicit_user_octocat():
    r = client.get("/", params={"users": "octocat"})
    assert r.status_code == 200
    assert isinstance(r.json(), list)
