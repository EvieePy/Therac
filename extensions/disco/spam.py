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
import datetime
import json
import logging
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

import core
from database.enums import ActionEnum, RuleEnum


if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

    from core.bots import DiscordBot
    from database.models import RuleWithExceptionModel
    from types_.database import ExceptionJsonT


type ChannelT = (
    discord.TextChannel
    | discord.ForumChannel
    | discord.CategoryChannel
    | discord.VoiceChannel
    | discord.DMChannel
    | discord.GroupChannel
    | discord.PartialMessageable
    | discord.StageChannel
    | discord.Thread
)
type MemberT = discord.Member | discord.User


LOGGER: logging.Logger = logging.getLogger(__name__)


class SpamCog(commands.Cog):
    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot
        self._multi_channel_cache: core.SpamCache[tuple[int, ...]] = core.SpamCache(cleanup_interval=15)
        self._tasks: set[asyncio.Task[None]] = set()
        self._action_mapping: dict[ActionEnum, Callable[..., Coroutine[None, None, None]]] = {
            ActionEnum.ban: self.do_ban,
            ActionEnum.kick: self.do_kick,
            ActionEnum.timeout: self.do_timeout,
            ActionEnum.warn: self.do_warn,
            ActionEnum.notify: self.do_notify,
        }

    async def cog_load(self) -> None: ...

    async def cog_unload(self) -> None:
        self._multi_channel_cache.close()

    def get_server_rules(
        self,
        type: RuleEnum,
        *,
        guild: discord.Guild | None = None,
        member: MemberT | None = None,
        channel: ChannelT | None = None,
    ) -> list[RuleWithExceptionModel] | None:
        # Guard we are actually in a server...
        if not guild or not isinstance(member, discord.Member):
            return

        # Don't run spam checks on mods/admins...
        perms = member.guild_permissions
        if perms.administrator or perms.ban_members:
            return

        rules = self.bot.rule_cache.get(guild.id, {}).get(type, None)
        return rules

    def is_exempt(
        self,
        rule: RuleWithExceptionModel,
        *,
        guild: discord.Guild | None = None,
        member: MemberT | None = None,
        channel: ChannelT | None = None,
    ) -> bool:
        exceptions: list[ExceptionJsonT] = json.loads(rule.exceptions)

        for exc in exceptions:
            type_id: int = exc["type_id"]

            if exc["type"] in ("member", "user") and member:
                if member.id == type_id:
                    return True

                joined: datetime.datetime | None = getattr(member, "joined_at", None)
                if not rule.max_age or not joined:
                    return False

                now = datetime.datetime.now(tz=datetime.UTC)
                return joined + datetime.timedelta(hours=rule.max_age) <= now

            elif exc["type"] in ("category", "channel") and channel:
                if channel.id == type_id:
                    return True

            elif exc["type"] == "role" and member:
                if type_id == 0:
                    return True

                for role in member.roles:  # type: ignore
                    if role.id == type_id:  # type: ignore
                        return True

        return False

    @commands.Cog.listener("on_message")
    async def channel_spam_message(self, message: discord.Message) -> None:
        guild = message.guild
        member = message.author
        channel = message.channel

        rules = self.get_server_rules(RuleEnum.channel_spam, guild=guild, member=member, channel=channel)
        if not rules:
            return

        assert guild, member

        for rule in rules:
            if self.is_exempt(rule, guild=guild, member=member, channel=channel):
                continue

            ttl = rule.per
            max_count = rule.total
            assert ttl and max_count

            key = (guild.id, member.id, rule.id)
            result = self._multi_channel_cache.upsert(key, ttl=ttl, max_count=max_count)

            if not result:
                continue

            self.do_action(rule, guild=guild, member=member, reason="Multi Channel Spam")

    @commands.Cog.listener("on_message")
    async def image_spam_message(self, message: discord.Message) -> None:
        guild = message.guild
        member = message.author
        channel = message.channel

        rules = self.get_server_rules(RuleEnum.image_spam, guild=guild, member=member, channel=channel)
        if not rules:
            return

        assert guild, member

        for rule in rules:
            if self.is_exempt(rule, guild=guild, member=member, channel=channel):
                continue

            total: int | None = rule.total
            if not total:
                continue

            count: int = len(
                [a for a in message.attachments if a.content_type in ("image/jpeg", "image/png", "image/gif", "image/webp")]
            )
            if count < total:
                continue

            self.do_action(rule, guild=guild, member=member, reason="Image Spam")

    def do_action(
        self,
        rule: RuleWithExceptionModel,
        *,
        guild: discord.Guild | None = None,
        member: MemberT | None = None,
        channel: ChannelT | None = None,
        reason: str,
    ) -> None:
        LOGGER.info("Rule (ID: %s) (%s) triggered for (%s, %s). Attempting action.", rule.id, rule.type, member, guild)
        coro = self._action_mapping.get(rule.action_type, None)

        if not coro:
            LOGGER.warning("Unknown action for rule (ID: %s): %s", rule.id, rule.action_type)
            return

        task = asyncio.create_task(coro(rule, guild=guild, member=member, channel=channel, reason=reason))
        task.add_done_callback(self._tasks.discard)
        self._tasks.add(task)

    async def do_ban(
        self,
        rule: RuleWithExceptionModel,
        *,
        guild: discord.Guild | None = None,
        member: MemberT | None = None,
        channel: ChannelT | None = None,
        reason: str,
    ) -> None:
        # TODO: Queue actions...
        assert isinstance(member, discord.Member)

        for _ in range(3):
            try:
                await member.ban(reason=f"AutoMod: {reason}")
                LOGGER.info("Successful do ban for rule %s for (%s, %s).", rule.id, member, guild)
                return
            except discord.NotFound:
                LOGGER.debug("Unable to do ban for rule %s for (%s, %s). Member not found.", rule.id, member, guild)
                break
            except discord.Forbidden:
                LOGGER.warning("Unable to do ban for rule %s for (%s, %s). Missing Permissions.", rule.id, member, guild)
                break
            except discord.HTTPException:
                await asyncio.sleep(11)

    async def do_kick(
        self,
        rule: RuleWithExceptionModel,
        *,
        guild: discord.Guild | None = None,
        member: MemberT | None = None,
        channel: ChannelT | None = None,
        reason: str,
    ) -> None: ...

    async def do_timeout(
        self,
        rule: RuleWithExceptionModel,
        *,
        guild: discord.Guild | None = None,
        member: MemberT | None = None,
        channel: ChannelT | None = None,
        reason: str,
    ) -> None: ...

    async def do_warn(
        self,
        rule: RuleWithExceptionModel,
        *,
        guild: discord.Guild | None = None,
        member: MemberT | None = None,
        channel: ChannelT | None = None,
        reason: str,
    ) -> None: ...

    async def do_notify(
        self,
        rule: RuleWithExceptionModel,
        *,
        guild: discord.Guild | None = None,
        member: MemberT | None = None,
        channel: ChannelT | None = None,
        reason: str,
    ) -> None: ...


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(SpamCog(bot))
