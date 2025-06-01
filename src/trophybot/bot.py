import trophybot.dice


class _Command:
    def __init__(self, callback):
        self.callback = callback


async def _roll_command(interaction):
    """Roll a d6 or pool as the generic /roll command."""
    # interaction.data.options is a list of option objects, or None/empty if no options.
    # In the test, it's a list (possibly empty) of SimpleNamespace objects.
    options_list = (
        interaction.data.options
        if hasattr(interaction.data, "options") and interaction.data.options is not None
        else []
    )

    parsed_options = {}
    if options_list:
        for opt in options_list:
            parsed_options[opt.name] = opt.value

    # Handle the case for "/roll" with no explicit options.
    # This corresponds to the "no_options_single_d6" test case.
    # README states: "if issued just as /roll, it rolls one d6 and reports the result"
    if not parsed_options:  # No options were provided by the user.
        result = trophybot.dice.roll_d6()  # Call the function from the dice module
        await interaction.response.send_message(f"🎲 You rolled: {result}")
        return

    light_dice_count = parsed_options.get("light")
    dark_dice_count = parsed_options.get("dark")

    # Scenario: /roll light=L (e.g., /roll light=3)
    # README: "if issued as /roll [light] (e.g. /roll 2), it rolls that many
    #          light-type d6s and reports the highest"
    # This also covers cases where dark_dice_count is explicitly 0.
    if light_dice_count is not None and (
        dark_dice_count is None or dark_dice_count == 0
    ):
        if light_dice_count == 0:  # Covered by "light_zero_dark_zero_via_light_option"
            await interaction.response.send_message("🎲 No dice rolled.")
            return
        if light_dice_count > 0:
            rolls = trophybot.dice.roll_pool(light_dice_count)
            highest = max(rolls) if rolls else "N/A"
            await interaction.response.send_message(
                f"🎲 Light dice ({light_dice_count}): {rolls} -> Highest: {highest}"
            )
            return

    # At this point, we are not in the "no options" case, nor in the "light dice only"
    # (or light dice with dark_dice_count=0) case.
    # This implies that dark_dice_count must be specified and > 0.

    if light_dice_count is None:
        # Case: /roll dark=D (light_dice_count is not specified)
        # This handles the "only_dark_specified" test.
        # If "light" option was not provided, "dark" must have been
        # (otherwise parsed_options is empty).
        # So, dark_dice_count is an int here.
        if dark_dice_count == 0 or dark_dice_count is None:
            await interaction.response.send_message("🎲 No dice rolled.")
            return
        # Now, dark_dice_count is an int and > 0.
        dark_rolls = trophybot.dice.roll_pool(dark_dice_count)
        highest_dark = max(dark_rolls)
        await interaction.response.send_message(
            f"🎲 Dark dice ({dark_dice_count}): {dark_rolls} -> Highest: {highest_dark}"
        )
        return
    else:
        # Case: /roll light=L dark=D
        # (light_dice_count is specified, dark_dice_count > 0)
        # light_dice_count can be 0 or > 0.
        # dark_dice_count is guaranteed to be > 0.
        # This handles "light_and_dark_*" tests and "light_zero_dark_gt_zero".

        light_rolls = []
        if light_dice_count > 0:
            light_rolls = trophybot.dice.roll_pool(light_dice_count)

        # In this branch, due to the preceding conditional structure:
        # - light_dice_count is a non-None int.
        # - dark_dice_count is a non-None int and dark_dice_count > 0.
        assert isinstance(dark_dice_count, int) and dark_dice_count > 0, (
            "Logical error: dark_dice_count should be a positive integer here."
        )
        dark_rolls = trophybot.dice.roll_pool(dark_dice_count)

        all_rolls_tagged = []
        # Add light rolls to list for consistent formatting, e.g., "Light (0): []"
        all_rolls_tagged.extend([(roll, "Light") for roll in light_rolls])
        all_rolls_tagged.extend([(roll, "Dark") for roll in dark_rolls])

        # Since dark_rolls is non-empty, all_rolls_tagged will be non-empty.
        highest_roll_val, highest_roll_type = max(all_rolls_tagged, key=lambda x: x[0])

        await interaction.response.send_message(
            f"🎲 Light ({light_dice_count}): {light_rolls}, Dark ({dark_dice_count}): {dark_rolls} -> Highest: {highest_roll_val} ({highest_roll_type})"  # noqa E501
        )
        return

    # As a final safeguard, though ideally all cases are covered above.
    # await interaction.response.send_message("Error: Unhandled roll combination.")


roll_command = _Command(_roll_command)
