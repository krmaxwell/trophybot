from types import SimpleNamespace

import pytest

from trophybot.bot import roll_command


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "options_data, dice_mocks, expected",
    [
        ([], {"roll_d6": lambda: 4}, "Die roll: 4"),
        (
            [{"name": "input", "value": "3"}],
            {
                "roll_pool": lambda c: (
                    [3, 5, 2] if c == 3 else pytest.fail(f"Unexpected {c}")
                )
            },
            "Dice rolls: 3 5 2 => Highest 5",
        ),
        (
            [{"name": "input", "value": "2 3"}],
            {
                "roll_pool": (
                    lambda rolls=[[2, 4], [2, 1, 4]]: lambda c: (
                        rolls.pop(0)
                        if (c == 2 and len(rolls) == 2) or (c == 3 and len(rolls) == 1)
                        else pytest.fail(f"Unexpected {c}")
                    )
                )(),
            },
            "Light rolls: 2 4 Dark rolls: 2 1 4 => Highest Dark 4",
        ),
    ],
)
async def test_roll_command(options_data, dice_mocks, expected, monkeypatch):
    if "roll_d6" in dice_mocks:
        monkeypatch.setattr("trophybot.dice.roll_d6", dice_mocks["roll_d6"])
    if "roll_pool" in dice_mocks:
        monkeypatch.setattr("trophybot.dice.roll_pool", dice_mocks["roll_pool"])

    responses = []

    async def fake_send(msg):
        responses.append(msg)

    fake_interaction = SimpleNamespace(
        response=SimpleNamespace(send_message=fake_send),
        data=SimpleNamespace(options=options_data),
    )

    await roll_command.callback(fake_interaction)
    assert responses == [expected]
