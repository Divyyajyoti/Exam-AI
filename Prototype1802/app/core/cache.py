import hashlib
import json
import time
from typing import Any, Optional

_CACHE: dict[str, tuple[Any, float]] = {}
TTL_SECONDS = 3600  # 1 hour


def make_key(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def get(key: str) -> Optional[Any]:
    item = _CACHE.get(key)
    if not item:
        return None
    value, ts = item
    if time.time() - ts > TTL_SECONDS:
        _CACHE.pop(key, None)
        return None
    return value


def set(key: str, value: Any) -> None:
    _CACHE[key] = (value, time.time())
