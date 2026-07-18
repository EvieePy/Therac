"""Copyright 2026-Present Evie. P.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import TYPE_CHECKING, Any, Self


if TYPE_CHECKING:
    from types_.cache import SpamCacheDataT


__all__ = ("SpamCache",)


LOGGER: logging.Logger = logging.getLogger(__name__)


class SpamCache[K]:
    def __init__(self, *, cleanup_interval: float) -> None:
        self._cleanup_interval = cleanup_interval
        self._cache: dict[K, SpamCacheDataT] = {}
        self._cleanup_task: asyncio.Task[None] = asyncio.create_task(self._background_clean())

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args: Any, **kwargs: Any) -> None:
        self.close()

    def close(self) -> None:
        self.reset()

        if not self._cleanup_task:
            return

        try:
            self._cleanup_task.cancel()
        except Exception as e:
            LOGGER.debug("Ignoring unhandled exception cancelling task: %s", e, exc_info=e)

    async def _background_clean(self) -> None:
        while True:
            await asyncio.sleep(self._cleanup_interval)
            self._remove_expired(time.monotonic())

    def _remove_expired(self, now: float, /) -> None:
        for key, value in self._cache.copy().items():
            if now >= value["expiry"]:
                self._cache.pop(key, None)

    def upsert(self, key: K, /, *, ttl: float, max_count: int) -> bool:
        now = time.monotonic()

        if max_count <= 1:
            raise ValueError("'max_count' parameter must be greater than 1.")
        if ttl <= 0:
            raise ValueError("'ttl' parameter must be greater than 0.")

        if not key in self._cache:
            self._cache[key] = {"count": 1, "max_count": max_count, "expiry": now + ttl}
            return False

        data: SpamCacheDataT = self._cache[key]
        if now >= data["expiry"]:
            self._cache[key] = {"count": 1, "max_count": max_count, "expiry": now + ttl}
            return False

        count = data["count"] + 1
        if count >= data["max_count"]:
            self._cache.pop(key, None)
            return True

        data["count"] = count
        return False

    def get(self, key: K, /) -> SpamCacheDataT | None:
        now = time.monotonic()

        if key not in self._cache:
            return

        data: SpamCacheDataT = self._cache[key]
        if now >= data["expiry"]:
            self._cache.pop(key, None)
            return

        return data

    def delete(self, key: K, /) -> None:
        self._cache.pop(key, None)

    def reset(self) -> None:
        self._cache = {}
