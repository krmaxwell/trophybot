"""Tests for zero dice handling in roll command."""

from types import SimpleNamespace

import pytest

from trophybot.bot import roll_command


@pytest.mark.asyncio
async def test_roll_light_zero_should_error():
    """Test that '/roll light 0' should return error message."""
    responses = []

    async def fake_send(msg):
        responses.append(msg)

    fake_interaction = SimpleNamespace(
        response=SimpleNamespace(send_message=fake_send),
        data=SimpleNamespace(options=[{"name": "input", "value": "light 0"}]),
    )

    await roll_command.callback(fake_interaction)

    # Should return error for zero dice
    actual_response = responses[0]
    assert actual_response == (
        "Please specify dice to roll (e.g. 'light 3', 'dark 2', 'light 1 dark 2')"
    )


@pytest.mark.asyncio
async def test_roll_dark_zero_should_error():
    """Test that '/roll dark 0' should return error message."""
    responses = []

    async def fake_send(msg):
        responses.append(msg)

    fake_interaction = SimpleNamespace(
        response=SimpleNamespace(send_message=fake_send),
        data=SimpleNamespace(options=[{"name": "input", "value": "dark 0"}]),
    )

    await roll_command.callback(fake_interaction)

    # Should return error for zero dice
    actual_response = responses[0]
    assert actual_response == (
        "Please specify dice to roll (e.g. 'light 3', 'dark 2', 'light 1 dark 2')"
    )


@pytest.mark.asyncio
async def test_roll_light_zero_dark_zero_should_error():
    """Test that '/roll light 0 dark 0' should return error message."""
    responses = []

    async def fake_send(msg):
        responses.append(msg)

    fake_interaction = SimpleNamespace(
        response=SimpleNamespace(send_message=fake_send),
        data=SimpleNamespace(options=[{"name": "input", "value": "light 0 dark 0"}]),
    )

    await roll_command.callback(fake_interaction)

    # Should return error for zero dice
    actual_response = responses[0]
    assert actual_response == (
        "Please specify dice to roll (e.g. 'light 3', 'dark 2', 'light 1 dark 2')"
    )
