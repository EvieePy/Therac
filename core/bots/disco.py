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

import logging
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from ..config import CONFIG


if TYPE_CHECKING:
    from database.enums import RuleEnum
    from database.models import RuleWithExceptionModel

    from ..manager import BotManager


LOGGER: logging.Logger = logging.getLogger(__name__)


class DiscordBot(commands.Bot):
    def __init__(self, manager: BotManager) -> None:
        self.manager = manager
        self.db = manager.db
        self.rule_cache: dict[int, dict[RuleEnum, list[RuleWithExceptionModel]]] = {}

        intents = discord.Intents.all()
        super().__init__(intents=intents, command_prefix=CONFIG["discord"]["prefixes"])

    async def process_cache(self) -> None:
        data: list[RuleWithExceptionModel] = await self.db.fetch_cache()

        for record in data:
            try:
                self.rule_cache[record.guild_id][record.type].append(record)
            except KeyError:
                self.rule_cache[record.guild_id] = {record.type: [record]}

    async def setup_hook(self) -> None:
        await self.process_cache()
        await self.load_extension("extensions.disco")

    async def on_ready(self) -> None:
        LOGGER.info("Logged into Discord: %s", self.user)
