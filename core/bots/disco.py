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

import logging

import discord
from discord.ext import commands

from ..config import CONFIG


LOGGER: logging.Logger = logging.getLogger(__name__)


class DiscordBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.all()
        super().__init__(intents=intents, command_prefix=CONFIG["discord"]["prefixes"])

    async def setup_hook(self) -> None: ...

    async def on_ready(self) -> None:
        LOGGER.info("Logged into Discord: %s", self.user)
