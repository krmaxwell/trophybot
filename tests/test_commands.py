# tests/test_commands.py
from types import SimpleNamespace

import pytest

from trophybot.bot import roll_command


@pytest.mark.asyncio
async def test_roll_command(monkeypatch):
    # patch the roll that roll_command will use
    monkeypatch.setattr("trophybot.bot.roll", lambda: 4)

    responses = []

    async def fake_send(message):
        responses.append(message)

    fake_response = SimpleNamespace(send_message=fake_send)
    fake_interaction = SimpleNamespace(response=fake_response)

    await roll_command.callback(fake_interaction)
    assert responses == ["🎲 You rolled: 4"]
