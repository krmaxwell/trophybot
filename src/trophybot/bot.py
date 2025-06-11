import re
import trophybot.dice


class _Command:
    def __init__(self, callback):
        self.callback = callback


async def _handle_single_d6_roll(interaction):
    """Roll a single d6."""
    result = trophybot.dice.roll_d6()
    return await interaction.response.send_message(f"Die roll: {result}")


async def _handle_pool_roll(interaction, count: int):
    """Roll ``count`` six-sided dice and report the highest."""
    if count <= 0:
        return await interaction.response.send_message("No dice rolled.")
    rolls = trophybot.dice.roll_pool(count)
    highest = max(rolls)
    return await interaction.response.send_message(
        f"Dice rolls: {' '.join(map(str, rolls))} => Highest {highest}"
    )


async def _handle_light_dark_roll(
    interaction, light_count: int, dark_count: int
):
    """Roll light and dark dice pools and report the highest with tie-breaking."""
    if light_count <= 0 and dark_count <= 0:
        return await interaction.response.send_message("No dice rolled.")

    light_rolls = trophybot.dice.roll_pool(light_count) if light_count > 0 else []
    dark_rolls = trophybot.dice.roll_pool(dark_count) if dark_count > 0 else []

    tagged = [(r, "Light") for r in light_rolls] + [
        (r, "Dark") for r in dark_rolls
    ]

    highest_val, highest_type = max(
        tagged, key=lambda x: (x[0], 1 if x[1] == "Dark" else 0)
    )

    parts = []
    if light_rolls:
        parts.append(f"Light rolls: {' '.join(map(str, light_rolls))}")
    if dark_rolls:
        parts.append(f"Dark rolls: {' '.join(map(str, dark_rolls))}")

    message = " ".join(parts) + f" => Highest {highest_type} {highest_val}"
    return await interaction.response.send_message(message)


def _extract_digits(options_list):
    """Return a list of digits found in the 'input' option string."""
    input_text = ""
    for opt in options_list or []:
        if opt.get("name") == "input":
            value = opt.get("value")
            if isinstance(value, str):
                input_text = value
            else:
                input_text = str(value)
            break
    return [int(d) for d in re.findall(r"\d", input_text)]


async def _roll_command(interaction):
    """Generic /roll command using a single text input option."""
    options = (
        interaction.data.options
        if hasattr(interaction.data, "options") and interaction.data.options is not None
        else []
    )

    digits = _extract_digits(options)

    if len(digits) == 0:
        return await _handle_single_d6_roll(interaction)
    if len(digits) == 1:
        return await _handle_pool_roll(interaction, digits[0])

    # Two or more digits - only first two matter
    return await _handle_light_dark_roll(interaction, digits[0], digits[1])


roll_command = _Command(_roll_command)


def _parse_combat_options(options_list):
    """Return a dict with dark dice count and endurance parsed from options."""
    parsed: dict[str, int] = {}
    for opt in options_list or []:
        name = opt["name"]
        value = opt["value"]
        if name in {"dark", "endurance"}:
            parsed[name] = value
    return parsed


async def _combat_command(interaction):
    """Handle the /combat endurance test."""
    options = (
        interaction.data.options
        if hasattr(interaction.data, "options") and interaction.data.options is not None
        else []
    )

    parsed_options = _parse_combat_options(options)

    dark_dice_count = parsed_options.get("dark")
    endurance_value = parsed_options.get("endurance")

    if dark_dice_count is None or endurance_value is None:
        return await interaction.response.send_message("Invalid options.")

    rolls = trophybot.dice.roll_pool(dark_dice_count)
    sorted_rolls = sorted(rolls, reverse=True)
    top_two = sorted_rolls[:2]
    total = sum(top_two)

    top_two_sorted = sorted(top_two)
    if len(top_two_sorted) == 1:
        top_line = f"Top 1: {top_two_sorted[0]} = {total}"
    else:
        top_line = f"Top 2: {top_two_sorted[0]}+{top_two_sorted[1]} = {total}"

    success = total >= endurance_value
    outcome = "Success" if success else "Failure"
    comparator = ">=" if success else "<"

    message = (
        f"Dice: {' '.join(map(str, rolls))}\n"
        f"{top_line}\n"
        f"Outcome: {outcome} ({comparator} {endurance_value})\n"
        "If any die matches your weak point, mark Ruin"
    )

    return await interaction.response.send_message(message)


combat_command = _Command(_combat_command)
