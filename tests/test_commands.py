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
            [{"name": "light", "value": 3}],
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
            [{"name": "dark", "value": 2}],
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
                {"name": "light", "value": 2},
                {"name": "dark", "value": 3},
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
                {"name": "light", "value": 1},
                {"name": "dark", "value": 2},
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
                {"name": "light", "value": 0},
                {"name": "dark", "value": 2},
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
                {"name": "light", "value": 2},
                {"name": "dark", "value": 0},
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
            [{"name": "light", "value": 0}],
            {},  # No dice functions should be called
            "🎲 No dice rolled.",
        ),
        (
            "light_zero_dark_zero_explicit",  # light=0, dark=0
            [
                {"name": "light", "value": 0},
                {"name": "dark", "value": 0},
            ],
            {},  # No dice functions should be called
            "🎲 No dice rolled.",
        ),
        (
            "light_and_dark_tie_dark_wins",  # light=2, dark=2, highest of each is 5
            [
                {"name": "light", "value": 2},
                {"name": "dark", "value": 2},
            ],
            {
                # This creates a stateful mock. The outer lambda is immediately called,
                # returning the inner lambda. The inner lambda closes over
                # 'rolls_to_return'.  It expects two calls with count=2, returning
                # predefined rolls.
                "roll_pool": (
                    lambda rolls_to_return=[[5, 1], [2, 5]]: lambda count_param: (
                        rolls_to_return.pop(0)
                        if count_param == 2 and rolls_to_return
                        else pytest.fail(
                            f"Unexpected roll_pool count: {count_param} or too many calls"  # noqa E501
                        )
                    )
                )(),
            },
            # Expected: Dark 5 wins due to tie-breaking rule
            "Light 5 1 Dark 2 5 => Dark 5 is highest",
        ),
        (
            "plain_text_two_numbers",  # user typed "/roll 2 3" as plain text
            [{"name": "text", "value": "2 3"}],
            {
                "roll_pool": lambda count: (
                    [1, 6]
                    if count == 2
                    else (
                        [2, 5, 3]
                        if count == 3
                        else pytest.fail(f"Unexpected roll_pool count: {count}")
                    )
                )
            },
            "Light 1 6 Dark 2 5 3 => Light 6 is highest",
        ),
        (
            "plain_text_one_number",  # user typed "/roll 2" as plain text
            [{"name": "text", "value": "2"}],
            {
                "roll_pool": lambda count: (
                    [2, 5, 1]
                    if count == 2
                    else pytest.fail(f"Unexpected roll_pool count: {count}")
                )
            },
            "Light 2 5 1 => Light 5 is highest",
        ),
        (
            "numbers_in_name",
            [
                {"name": "2", "value": ""},
                {"name": "3", "value": ""},
            ],
            {
                "roll_pool": lambda count: (
                    [1, 6]
                    if count == 2
                    else (
                        [2, 4, 5]
                        if count == 3
                        else pytest.fail(f"Unexpected roll_pool count: {count}")
                    )
                )
            },
            "Light 1 6 Dark 2 4 5 => Light 6 is highest",
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
        "light_and_dark_tie_dark_wins",
        "plain_text_two_numbers",
        "plain_text_one_number",
        "numbers_in_name",
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

    # We need to reset responses for each parameterized test run,
    # especially for mocks that depend on call order/count like the new tie test.
    # The `responses` list is captured by `fake_send_message` closure.
    # A more robust way for call order dependent mocks might involve a class-based mock
    # or a more sophisticated counter, but for now, checking len(responses) works.
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
