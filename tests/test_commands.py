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
    # force the RNG
    monkeypatch.setattr("trophybot.dice.roll_d6", lambda: 4)

    # create a fake ctx
    ctx = commands.Context(
        prefix="!",
        bot=bot,
        message=cast(Message, SimpleNamespace(_state=None)),
        view=StringView(""),
    )
    # capture sends
    sent = []
    monkeypatch.setattr(ctx, "send", lambda msg: sent.append(msg))

    # call the command
    await roll_d6_command(ctx)
    assert sent == ["🎲 You rolled: 4"]
