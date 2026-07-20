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
import pathlib
import re
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from core.bots import DiscordBot


LOGGER: logging.Logger = logging.getLogger(__name__)
EXT_PATTERN: re.Pattern[str] = re.compile(r"^[a-zA-Z0-9_]+\.py$")


async def setup(bot: DiscordBot) -> None:
    ext_path = pathlib.Path("extensions/disco")
    exts = [e for e in ext_path.iterdir() if e.is_file() and EXT_PATTERN.match(e.name) and not e.name.startswith("_")]
    loaded: list[str] = []

    for ext in exts:
        try:
            await bot.load_extension(f"extensions.disco.{ext.stem}")
        except Exception as e:
            LOGGER.critical("Failed to load extension %r: %s", ext.name, e)
        else:
            loaded.append(ext.name)

    if loaded:
        LOGGER.info("Successfully loaded extensions: %s", loaded)


async def teardown(bot: DiscordBot) -> None:
    exts = bot.extensions
    unloaded: list[str] = []

    for ext in exts:
        try:
            await bot.unload_extension(ext, package="extensions.disco")
        except Exception as e:
            LOGGER.critical("Failed to unload extension %r: %s", ext, e)
        else:
            unloaded.append(ext)

    if unloaded:
        LOGGER.info("Successfully unloaded extensions: %s", unloaded)
