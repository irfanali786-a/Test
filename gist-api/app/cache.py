# app/cache.py
import time
import asyncio
from typing import Any, Dict, Optional

class TTLCache:
    def __init__(self, ttl_seconds: int = 30):
        self._ttl = ttl_seconds
        self._data: Dict[str, tuple[float, Any]] = {}
        self._lock = asyncio.Lock()

    async def _cleanup(self):
        now = time.time()
        keys = [k for k, (ts, _) in self._data.items() if now - ts > self._ttl]
        for k in keys:
            self._data.pop(k, None)

    def get(self, key: str) -> Optional[Any]:
        # synchronous get to keep usage simple in FastAPI route
        now = time.time()
        item = self._data.get(key)
        if not item:
            return None
        ts, value = item
        if now - ts > self._ttl:
            self._data.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        self._data[key] = (time.time(), value)
