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

import asyncio
import logging
from typing import Any, Self

import asyncpg

from .enums import *
from .models import *


type PoolT = asyncpg.Pool[asyncpg.Record]
LOGGER: logging.Logger = logging.getLogger(__name__)


__all__ = ("Database",)


class Database:
    pool: PoolT

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args: Any, **kwargs: Any) -> None:
        await self.close()

    async def connect(self, dsn: str, /, *, min_size: int = 10, max_size: int = 100) -> None:
        self.pool = await asyncpg.create_pool(dsn, min_size=min_size, max_size=max_size)

        with open("database/schema.sql") as fp:
            await self.pool.execute(fp.read())

        LOGGER.info("Successfully connected to %r.", self)

    async def close(self) -> None:
        pool: PoolT | None = getattr(self, "pool", None)
        if not pool:
            return

        try:
            async with asyncio.timeout(10):
                await pool.close()
        except TimeoutError:
            LOGGER.warning("Unable to gracefully close %r. Forcefully terminating.", self)
            pool.terminate()
        except Exception as e:
            LOGGER.warning("Unhandled exception while gracefully closing %r: %s", self, e)
        else:
            LOGGER.info("Gracefully closed %r.", self)

    async def fetch_cache(self) -> list[RuleWithExceptionModel]:
        query = """SELECT
                    r.id,
                    r.name,
                    r.guild_id,
                    r.type,
                    r.action_type,
                    r.regex,
                    r.rate,
                    r.per,
                    r.total,
                    r.max_age,
                    COALESCE(
                        jsonb_agg(jsonb_build_object('type', e.type,'type_id', e.type_id))
                        FILTER (WHERE e.id IS NOT NULL), '[]'::jsonb) AS exceptions
                FROM rules AS r
                LEFT JOIN exceptions AS e
                    ON e.rule_id = r.id
                GROUP BY r.id;
        """

        async with self.pool.acquire() as connection:
            data: list[RuleWithExceptionModel] = await connection.fetch(query, record_class=RuleWithExceptionModel)

        return data

    async def fetch_rules(self) -> ...: ...

    async def fetch_guild_rules(self, *, guild_id: int, type: RuleEnum) -> list[RuleModel]: ...
