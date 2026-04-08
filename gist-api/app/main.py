# app/main.py
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import httpx
import asyncio
from typing import List, Dict, Any
from .cache import TTLCache

app = FastAPI(title="Gist List API", version="1.0")

# Simple in-memory TTL cache (user -> (timestamp, data))
cache = TTLCache(ttl_seconds=30)  # 30s cache to reduce GitHub calls

class GistOut(BaseModel):
    id: str
    html_url: str
    description: str | None
    files: List[str]

GITHUB_API = "https://api.github.com"

async def fetch_gists_from_github(username: str) -> List[Dict[str, Any]]:
    url = f"{GITHUB_API}/users/{username}/gists"
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, headers={"Accept": "application/vnd.github+json"})
    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="GitHub user not found")
    if resp.status_code >= 400:
        raise HTTPException(status_code=resp.status_code, detail="GitHub API error")
    return resp.json()

def simplify_gist(g: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": g.get("id"),
        "html_url": g.get("html_url"),
        "description": g.get("description"),
        "files": list(g.get("files", {}).keys()),
    }

@app.get("/", response_model=List[GistOut])
async def list_gists(user: str = Query("octocat", description="GitHub username")):
    """
    Return a list of public gists for the given GitHub username.
    Default user is 'octocat'.
    """
    # Try cache
    cached = cache.get(user)
    if cached is not None:
        return cached

    # Fetch from GitHub
    gists = await fetch_gists_from_github(user)
    simplified = [simplify_gist(g) for g in gists]
    cache.set(user, simplified)
    return simplified

# Health endpoint
@app.get("/health")
def health():
    return {"status": "ok"}