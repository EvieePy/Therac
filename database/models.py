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

from functools import cache
from typing import Any

import asyncpg

from .enums import *


__all__ = ("BaseModel", "ExceptionModel", "RuleModel", "RuleWithExceptionModel")


class BaseModel(asyncpg.Record):
    @cache
    def __getattr__(self, name: str) -> Any:
        return self[name]


class RuleModel(BaseModel):
    id: int
    name: str
    guild_id: int
    type: RuleEnum
    action_type: ActionEnum
    regex: str | None
    rate: int | None
    per: int | None
    total: int | None
    max_age: int | None


class ExceptionModel(BaseModel):
    id: int
    rule_id: int
    type: SnowflakeEnum
    type_id: int


class RuleWithExceptionModel(BaseModel):
    id: int
    name: str
    guild_id: int
    type: RuleEnum
    action_type: ActionEnum
    regex: str | None
    rate: int | None
    per: int | None
    total: int | None
    max_age: int | None
    exceptions: str
