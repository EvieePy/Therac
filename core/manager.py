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

from typing import TYPE_CHECKING, Any, Self

from core import bots

from .config import CONFIG


if TYPE_CHECKING:
    from database import Database


__all__ = ("BotManager",)


class BotManager:
    dbot: bots.DiscordBot
    tbot: bots.TwitchBot

    def __init__(self, *, database: Database) -> None:
        self.db = database

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args: Any, **kwargs: Any) -> None:
        await self.close()

    async def run(self) -> None:
        self.dbot = bots.DiscordBot(self)
        self.tbot = bots.TwitchBot(self)

        async with self.dbot, self.tbot:
            await self.tbot.login()
            await self.dbot.start(token=CONFIG["discord"]["token"])

    async def close(self) -> None: ...
