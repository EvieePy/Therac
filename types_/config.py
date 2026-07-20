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

from typing import TypedDict


class GeneralConfigT(TypedDict):
    logging_level: int


class DiscordConfigT(TypedDict):
    token: str
    prefixes: list[str]


class TwitchConfigT(TypedDict):
    client_id: str
    client_secret: str
    bot_id: str
    owner_id: str
    prefix: list[str]


class DatabaseConfigT(TypedDict):
    dsn: str
    min_size: int
    max_size: int


class ConfigT(TypedDict):
    general: GeneralConfigT
    database: DatabaseConfigT
    discord: DiscordConfigT
    twitch: TwitchConfigT
