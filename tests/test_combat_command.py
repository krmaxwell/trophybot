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


@pytest.mark.asyncio
async def test_combat_command_missing_dark_option():
    """Should return error message when dark option is missing."""
    responses = []

    async def fake_send(message):
        responses.append(message)

    fake_interaction = SimpleNamespace(
        response=SimpleNamespace(send_message=fake_send),
        data=SimpleNamespace(
            options=[
                {"name": "endurance", "value": 9}
                # Missing "dark" option
            ]
        ),
    )

    await combat_command.callback(fake_interaction)
    assert responses == ["Invalid options."]


@pytest.mark.asyncio
async def test_combat_command_missing_endurance_option():
    """Should return error message when endurance option is missing."""
    responses = []

    async def fake_send(message):
        responses.append(message)

    fake_interaction = SimpleNamespace(
        response=SimpleNamespace(send_message=fake_send),
        data=SimpleNamespace(
            options=[
                {"name": "dark", "value": 3}
                # Missing "endurance" option
            ]
        ),
    )

    await combat_command.callback(fake_interaction)
    assert responses == ["Invalid options."]


@pytest.mark.asyncio
async def test_combat_command_no_options():
    """Should return error message when no options provided."""
    responses = []

    async def fake_send(message):
        responses.append(message)

    fake_interaction = SimpleNamespace(
        response=SimpleNamespace(send_message=fake_send),
        data=SimpleNamespace(options=[]),
    )

    await combat_command.callback(fake_interaction)
    assert responses == ["Invalid options."]


@pytest.mark.asyncio
async def test_combat_command_single_die_roll(monkeypatch):
    """Should handle single die roll correctly (Top 1 format)."""
    monkeypatch.setattr("trophybot.dice.roll_pool", lambda count: [4])

    responses = []

    async def fake_send(message):
        responses.append(message)

    fake_interaction = SimpleNamespace(
        response=SimpleNamespace(send_message=fake_send),
        data=SimpleNamespace(
            options=[
                {"name": "dark", "value": 1},
                {"name": "endurance", "value": 6},
            ]
        ),
    )

    await combat_command.callback(fake_interaction)

    expected = (
        "Dice: 4\n"
        "Top 1: 4 = 4\n"
        "Outcome: Failure (< 6)\n"
        "If any die matches your weak point, mark Ruin"
    )
    assert responses == [expected]


@pytest.mark.asyncio
async def test_combat_command_zero_dice_count(monkeypatch):
    """Should handle zero dice count gracefully without crashing."""
    monkeypatch.setattr("trophybot.dice.roll_pool", lambda count: [])

    responses = []

    async def fake_send(message):
        responses.append(message)

    fake_interaction = SimpleNamespace(
        response=SimpleNamespace(send_message=fake_send),
        data=SimpleNamespace(
            options=[
                {"name": "dark", "value": 0},
                {"name": "endurance", "value": 5},
            ]
        ),
    )

    await combat_command.callback(fake_interaction)

    # Should handle empty dice gracefully and return a proper response
    assert len(responses) == 1
    response = responses[0]
    assert "Dice:" in response
    assert "Outcome:" in response
    # Should show failure when rolling 0 dice vs any target
    assert "Failure" in response


@pytest.mark.asyncio
async def test_combat_command_negative_dice_count():
    """Should handle negative dice count appropriately."""
    responses = []

    async def fake_send(message):
        responses.append(message)

    fake_interaction = SimpleNamespace(
        response=SimpleNamespace(send_message=fake_send),
        data=SimpleNamespace(
            options=[
                {"name": "dark", "value": -1},
                {"name": "endurance", "value": 5},
            ]
        ),
    )

    # Should either reject negative values or handle gracefully
    try:
        await combat_command.callback(fake_interaction)

        # If it accepts negative values, should not crash
        assert len(responses) == 1

    except (ValueError, IndexError):
        # Acceptable to reject negative dice counts
        pass
