"""
FILE: data/api/redis_db.py
ROLE: Concrete Redis implementation of BaseDB.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Iterable, Tuple

import redis

from data.api.reddis_api_db import BaseDB  # Import the abstract base class


class RedisDB(BaseDB):
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
    ) -> None:
        self._client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=False,
        )

    def _dumps(self, value: Any) -> str:
        return json.dumps(value)

    def _loads(self, raw: Optional[bytes]) -> Optional[Any]:
        if raw is None:
            return None
        if isinstance(raw, (bytes, bytearray)):
            s = raw.decode("utf-8")
        else:
            s = str(raw)
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            return s

    def _scan_keys(self, pattern: str) -> List[str]:
        cursor: int = 0
        out: List[str] = []
        while True:
            cursor, batch = self._client.scan(cursor=cursor, match=pattern, count=1000)
            for k in batch:
                out.append(k.decode("utf-8") if isinstance(k, (bytes, bytearray)) else str(k))
            if cursor == 0:
                break
        return out

    def get(self, key: str) -> Optional[Any]:
        raw = self._client.get(key)
        return self._loads(raw)

    def set(self, key: str, value: Any) -> bool:
        payload = self._dumps(value)
        return bool(self._client.set(key, payload))

    def delete(self, key: str) -> bool:
        return int(self._client.delete(key)) > 0

    def exists(self, key: str) -> bool:
        return int(self._client.exists(key)) > 0

    def keys(self, pattern: str = "*") -> List[str]:
        return self._scan_keys(pattern)

    def get_all(self, pattern: str = "*") -> Dict[str, Any]:
        ks = self._scan_keys(pattern)
        if not ks:
            return {}

        pipe = self._client.pipeline()
        for k in ks:
            pipe.get(k)
        values = pipe.execute()

        out: Dict[str, Any] = {}
        for k, raw in zip(ks, values):
            out[k] = self._loads(raw)
        return out

    def clear(self) -> bool:
        return bool(self._client.flushdb())

    def set_many(self, items: Dict[str, Any]) -> bool:
        if not items:
            return True
        pipe = self._client.pipeline()
        for k, v in items.items():
            pipe.set(k, self._dumps(v))
        results = pipe.execute()
        return all(bool(r) for r in results)

    def delete_many(self, pattern: str) -> int:
        deleted = 0
        cursor: int = 0
        while True:
            cursor, batch = self._client.scan(cursor=cursor, match=pattern, count=1000)
            if batch:
                pipe = self._client.pipeline()
                for k in batch:
                    pipe.delete(k)
                res = pipe.execute()
                deleted += sum(int(x) for x in res)
            if cursor == 0:
                break
        return deleted

    def ping(self) -> bool:
        return bool(self._client.ping())

