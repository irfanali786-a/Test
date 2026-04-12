# app/main.py
from fastapi import FastAPI, HTTPException, Query, Request
from pydantic import BaseModel
import httpx
from typing import List, Dict, Any
from .cache import TTLCache
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

app = FastAPI(title="Gist List API", version="1.0")

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Simple in-memory TTL cache (user -> (timestamp, data))
cache = TTLCache(ttl_seconds=30)  # 30s cache to reduce GitHub calls

class GistOut(BaseModel):
    id: str
    html_url: str
    description: str | None
    files: List[str]
    owner: str

GITHUB_API = "https://api.github.com"

async def fetch_gists_from_github(username: str, page: int = 1, per_page: int = 30) -> List[Dict[str, Any]]:
    url = f"{GITHUB_API}/users/{username}/gists"
    params = {"page": page, "per_page": per_page}
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, headers={"Accept": "application/vnd.github+json"}, params=params)
    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="GitHub user not found")
    if resp.status_code >= 400:
        raise HTTPException(status_code=resp.status_code, detail="GitHub API error")
    return resp.json()

def simplify_gist(g: Dict[str, Any], username: str) -> Dict[str, Any]:
    return {
        "id": g.get("id"),
        "html_url": g.get("html_url"),
        "description": g.get("description"),
        "files": list(g.get("files", {}).keys()),
        "owner": g.get("owner", {}).get("login", username),
    }

@app.get("/", response_model=List[GistOut])
@limiter.limit("10/minute")
async def list_gists(
    request: Request,
    users: str = Query("octocat", description="Comma-separated list of GitHub usernames"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(30, ge=1, le=100, description="Number of gists per page")
):
    """
    Return a list of public gists for the given GitHub usernames.
    Supports pagination with page and per_page parameters.
    Supports multiple users by comma-separating usernames.
    Default users 'octocat', page 1, per_page 30.
    Rate limited to 10 requests per minute.
    """
    user_list = [u.strip() for u in users.split(",") if u.strip()]
    cache_key = f"{users}_{page}_{per_page}"
    # Try cache
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    all_gists = []
    for username in user_list:
        # Fetch from GitHub
        gists = await fetch_gists_from_github(username, page, per_page)
        for g in gists:
            simplified = simplify_gist(g, username)
            all_gists.append(simplified)

    cache.set(cache_key, all_gists)
    return all_gists

# Health endpoint
@app.get("/health")
def health():
    return {"status": "ok"}