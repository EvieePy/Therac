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

import enum


__all__ = ("ActionEnum", "RuleEnum", "SnowflakeEnum")


# fmt: off
class SnowflakeEnum(enum.StrEnum):
    guild    = "guild"
    category = "category"
    channel  = "channel"
    role     = "role"
    user     = "user"
    member   = "member"


class RuleEnum(enum.StrEnum):
    channel_spam = "channel_spam"
    image_spam   = "image_spam"
    mention_spam = "mention_spam"
    url_spam     = "url_spam"
    general_spam = "general_spam"


class ActionEnum(enum.StrEnum):
    notify  = "notify"
    warn    = "warn"
    timeout = "timeout"
    kick    = "kick"
    ban     = "ban"
