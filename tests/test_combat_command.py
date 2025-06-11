from types import SimpleNamespace

import pytest

from trophybot.bot import combat_command


@pytest.mark.asyncio
async def test_combat_command_failure(monkeypatch):
    monkeypatch.setattr("trophybot.dice.roll_pool", lambda count: [2, 3, 5])

    responses = []

    async def fake_send(message):
        responses.append(message)

    fake_interaction = SimpleNamespace(
        response=SimpleNamespace(send_message=fake_send),
        data=SimpleNamespace(
            options=[
                {"name": "dark", "value": 3},
                {"name": "endurance", "value": 9},
            ]
        ),
    )

    await combat_command.callback(fake_interaction)

    expected = (
        "Dice: 2 3 5\n"
        "Top 2: 3+5 = 8\n"
        "Outcome: Failure (< 9)\n"
        "If any die matches your weak point, mark Ruin"
    )
    assert responses == [expected]


@pytest.mark.asyncio
async def test_combat_command_success(monkeypatch):
    monkeypatch.setattr("trophybot.dice.roll_pool", lambda count: [4, 6])

    responses = []

    async def fake_send(message):
        responses.append(message)

    fake_interaction = SimpleNamespace(
        response=SimpleNamespace(send_message=fake_send),
        data=SimpleNamespace(
            options=[
                {"name": "dark", "value": 2},
                {"name": "endurance", "value": 9},
            ]
        ),
    )

    await combat_command.callback(fake_interaction)

    expected = (
        "Dice: 4 6\n"
        "Top 2: 4+6 = 10\n"
        "Outcome: Success (>= 9)\n"
        "If any die matches your weak point, mark Ruin"
    )
    assert responses == [expected]
