# tests/test_commands.py
from types import SimpleNamespace
from typing import cast

import pytest
from discord import Message
from discord.ext import commands
from discord.ext.commands.view import StringView

from trophybot.bot import bot, roll_d6_command


@pytest.mark.asyncio
async def test_roll_d6_command(monkeypatch):
    # patch the roll_d6 that roll_d6_command will use:
    monkeypatch.setattr("trophybot.bot.roll_d6", lambda: 4)

    # create a fake ctx, casting the SimpleNamespace to Message
    fake_msg = cast(Message, SimpleNamespace(_state=None))
    ctx = commands.Context(
        prefix="!",
        bot=bot,
        message=fake_msg,
        view=StringView(""),
    )

    # capture sends with an async stub
    sent = []

    async def fake_send(msg):
        sent.append(msg)

    monkeypatch.setattr(ctx, "send", fake_send)

    # call the command
    await roll_d6_command(ctx)
    assert sent == ["🎲 You rolled: 4"]
