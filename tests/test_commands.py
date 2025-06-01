# tests/test_commands.py
from types import SimpleNamespace

import pytest

from trophybot.bot import roll_command


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "test_id, options_data, dice_mocks, expected_message",
    [
        (
            "no_options_single_d6",
            [],
            {"roll_d6": lambda: 4},
            "🎲 You rolled: 4",
        ),
        (
            "only_light_gt_1",
            [SimpleNamespace(name="light", value=3)],
            {
                "roll_pool": lambda count: (
                    [2, 5, 1]
                    if count == 3
                    else pytest.fail(f"Unexpected roll_pool count: {count}")
                )
            },
            "Light 2 5 1 => Light 5 is highest",
        ),
        (
            "only_dark_specified",  # User issues /roll dark=D, means 0 light dice.
            [SimpleNamespace(name="dark", value=2)],
            {
                "roll_pool": lambda count: (
                    [4, 1]
                    if count == 2  # Only dark dice pool should be rolled
                    else pytest.fail(f"Unexpected roll_pool count: {count}")
                )
            },
            "Dark 4 1 => Dark 4 is highest",
        ),
        (
            "light_and_dark_light_highest",  # light=2, dark=3
            [
                SimpleNamespace(name="light", value=2),
                SimpleNamespace(name="dark", value=3),
            ],
            {
                "roll_pool": lambda count: (
                    [1, 6]
                    if count == 2
                    else (
                        [2, 5, 3]
                        if count == 3
                        else pytest.fail(f"Unexpected roll_pool count: {count}")
                    )
                ),
            },
            "Light 1 6 Dark 2 5 3 => Light 6 is highest",
        ),
        (
            "light_and_dark_dark_highest",  # light=1, dark=2
            [
                SimpleNamespace(name="light", value=1),
                SimpleNamespace(name="dark", value=2),
            ],
            {
                "roll_pool": lambda count: (
                    [3]
                    if count == 1
                    else (
                        [4, 1]
                        if count == 2
                        else pytest.fail(f"Unexpected roll_pool count: {count}")
                    )
                ),
            },
            "Light 3 Dark 4 1 => Dark 4 is highest",
        ),
        (
            "light_zero_dark_gt_zero",  # light=0, dark=2
            [
                SimpleNamespace(name="light", value=0),
                SimpleNamespace(name="dark", value=2),
            ],
            {
                "roll_pool": lambda count: (
                    [4, 1]
                    if count == 2
                    else pytest.fail(f"Unexpected roll_pool count: {count}")
                )
            },
            # If light dice are 0, they are not mentioned in the roll list
            "Dark 4 1 => Dark 4 is highest",
        ),
        (
            "light_gt_zero_dark_zero",  # light=2, dark=0 (explicitly)
            [
                SimpleNamespace(name="light", value=2),
                SimpleNamespace(name="dark", value=0),
            ],
            {
                "roll_pool": lambda count: (
                    [2, 5, 1]
                    if count == 2
                    else pytest.fail(f"Unexpected roll_pool count: {count}")
                )
            },
            # If dark dice are 0, they are not mentioned
            "Light 2 5 1 => Light 5 is highest",
        ),
        (
            "light_zero_dark_zero_via_light_option",  # light=0 (dark defaults to 0)
            [SimpleNamespace(name="light", value=0)],
            {},  # No dice functions should be called
            "🎲 No dice rolled.",
        ),
        (
            "light_zero_dark_zero_explicit",  # light=0, dark=0
            [
                SimpleNamespace(name="light", value=0),
                SimpleNamespace(name="dark", value=0),
            ],
            {},  # No dice functions should be called
            "🎲 No dice rolled.",
        ),
    ],
    ids=[
        "no_options_single_d6",
        "only_light_gt_1",
        "only_dark_specified",
        "light_and_dark_light_highest",
        "light_and_dark_dark_highest",
        "light_zero_dark_gt_zero",
        "light_gt_zero_dark_zero",
        "light_zero_dark_zero_via_light_option",
        "light_zero_dark_zero_explicit",
    ],
)
async def test_roll_command_scenarios(
    monkeypatch, test_id, options_data, dice_mocks, expected_message
):
    """Tests the /roll command callback with various options and mock dice rolls."""

    # Apply mocks for dice functions in trophybot.dice module
    # The _roll_command in trophybot.bot will be updated to use these.
    if "roll_d6" in dice_mocks:
        monkeypatch.setattr("trophybot.dice.roll_d6", dice_mocks["roll_d6"])
    if "roll_pool" in dice_mocks:
        monkeypatch.setattr("trophybot.dice.roll_pool", dice_mocks["roll_pool"])

    responses = []

    async def fake_send_message(message):
        responses.append(message)

    # Simulate the interaction object structure
    # The command handler receives an interaction object.
    # We assume options are accessed via interaction.data.options
    fake_interaction_data = SimpleNamespace(options=options_data)
    fake_interaction = SimpleNamespace(
        response=SimpleNamespace(send_message=fake_send_message),
        data=fake_interaction_data,
    )

    await roll_command.callback(fake_interaction)
    assert responses == [expected_message], f"Test case {test_id} failed."
