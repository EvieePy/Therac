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

import twitchio

import core
import database


LOGGER: logging.Logger = logging.getLogger(__name__)


def main() -> None:
    twitchio.utils.setup_logging(level=core.CONFIG["general"]["logging_level"])

    async def runner() -> None:
        async with database.Database() as db, core.BotManager(database=db) as manager:
            await db.connect(core.CONFIG["database"]["dsn"])
            await manager.run()

    try:
        asyncio.run(runner())
    except KeyboardInterrupt:
        LOGGER.warning("Shutting down due to KeyboardInterrupt.")
    except Exception as e:
        LOGGER.critical("Shutting down due to unexcepected error: %s.", e, exc_info=e)


if __name__ == "__main__":
    main()
