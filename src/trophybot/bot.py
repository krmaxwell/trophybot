import trophybot.dice


class _Command:
    def __init__(self, callback):
        self.callback = callback


async def _handle_single_d6_roll(interaction):
    """Handle rolling a single d6 when no options are provided."""
    result = trophybot.dice.roll_d6()
    return await interaction.response.send_message(f"🎲 You rolled: {result}")


async def _handle_light_dice_roll(interaction, light_dice_count: int):
    """Handle rolling light dice when dark dice are not involved or are zero."""
    # Precondition: light_dice_count > 0
    rolls = trophybot.dice.roll_pool(light_dice_count)
    highest = max(rolls)
    return await interaction.response.send_message(
        f"Light {' '.join(map(str, rolls))} => Light {highest} is highest"
    )


async def _handle_dark_dice_roll(interaction, dark_dice_count: int):
    """Handle rolling dark dice when light dice are not specified or are zero."""
    # Precondition: dark_dice_count > 0
    dark_rolls = trophybot.dice.roll_pool(dark_dice_count)
    highest_dark = max(dark_rolls)
    return await interaction.response.send_message(
        f"Dark {' '.join(map(str, dark_rolls))} => Dark {highest_dark} is highest"
    )


async def _handle_combined_dice_roll(
    interaction, light_dice_count: int, dark_dice_count: int
):
    """Handle rolling both light and dark dice."""
    # Preconditions: dark_dice_count > 0. light_dice_count >= 0.
    light_rolls = []
    if light_dice_count > 0:
        light_rolls = trophybot.dice.roll_pool(light_dice_count)

    # dark_dice_count is > 0
    assert isinstance(dark_dice_count, int) and dark_dice_count > 0, (
        "Logical error: dark_dice_count should be a positive integer here."
    )
    dark_rolls = trophybot.dice.roll_pool(dark_dice_count)

    all_rolls_tagged = []
    # We only add light rolls to all_rolls_tagged if light_dice_count > 0
    all_rolls_tagged.extend([(roll, "Light") for roll in light_rolls])
    all_rolls_tagged.extend([(roll, "Dark") for roll in dark_rolls])

    # Since dark_rolls is non-empty, all_rolls_tagged will be non-empty.
    # To handle ties where dark dice win, we use a tuple as the key for max().
    # The 1st element is the roll value, the 2nd is a preference score (Dark > Light)
    highest_roll_val, highest_roll_type = max(
        all_rolls_tagged, key=lambda x: (x[0], 1 if x[1] == "Dark" else 0)
    )

    message_parts = []
    if light_rolls:  # True if light_dice_count > 0
        message_parts.append(f"Light {' '.join(map(str, light_rolls))}")
    message_parts.append(
        f"Dark {' '.join(map(str, dark_rolls))}"
    )  # dark_rolls is never empty here

    roll_summary_str = " ".join(message_parts)
    return await interaction.response.send_message(
        f"{roll_summary_str} => {highest_roll_type} {highest_roll_val} is highest"
    )


async def _roll_command(interaction):
    """Roll a d6 or pool as the generic /roll command."""
    options_list = (
        interaction.data.options
        if hasattr(interaction.data, "options") and interaction.data.options is not None
        else []
    )

    parsed_options = {}
    if options_list:
        for opt in options_list:
            parsed_options[opt["name"]] = opt["value"]

    light_dice_count = parsed_options.get("light")
    dark_dice_count = parsed_options.get("dark")

    # Case 1: No options provided (plain /roll)
    if light_dice_count is None and dark_dice_count is None:
        return await _handle_single_d6_roll(interaction)
    # Case 2: Light dice specified, dark dice are zero or not specified
    elif light_dice_count is not None and (
        dark_dice_count is None or dark_dice_count == 0
    ):
        if light_dice_count == 0:
            return await interaction.response.send_message("🎲 No dice rolled.")
        else:  # light_dice_count > 0
            return await _handle_light_dice_roll(interaction, light_dice_count)
    # Case 3: Dark dice specified, light dice are not specified
    # (dark_dice_count must be non-None here due to previous conditions)
    elif light_dice_count is None:
        # dark_dice_count is guaranteed to be non-None here, otherwise Case 1 applies.
        if dark_dice_count == 0:
            return await interaction.response.send_message("🎲 No dice rolled.")
        else:  # dark_dice_count > 0
            return await _handle_dark_dice_roll(interaction, dark_dice_count)  # type: ignore
    # Case 4: Both light and dark dice are specified, and dark_dice_count > 0
    # (light_dice_count can be >= 0 here)
    else:
        # This implies:
        # - light_dice_count is not None (it's an int, could be 0)
        # - dark_dice_count is not None and dark_dice_count > 0
        #   (if dark_dice_count was 0, it would have been caught by Case 2)
        return await _handle_combined_dice_roll(
            interaction,
            light_dice_count,
            dark_dice_count,  # type: ignore
        )


roll_command = _Command(_roll_command)

