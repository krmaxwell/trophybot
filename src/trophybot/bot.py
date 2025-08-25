import re
from typing import Any, List, Optional, Tuple, Union

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


async def _handle_light_dark_roll(interaction, light_count: int, dark_count: int):
    """Roll light and dark dice pools and report the highest with tie-breaking."""
    if light_count <= 0 and dark_count <= 0:
        return await interaction.response.send_message("No dice rolled.")

    light_rolls = trophybot.dice.roll_pool(light_count) if light_count > 0 else []
    dark_rolls = trophybot.dice.roll_pool(dark_count) if dark_count > 0 else []

    tagged = [(r, "Light") for r in light_rolls] + [(r, "Dark") for r in dark_rolls]

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


def _parse_light_dark_input(text: str) -> Optional[Tuple[int, int]]:
    """Parse 'light X dark Y' format in any order."""
    words = text.lower().split()
    light_count, dark_count = 0, 0

    for i, word in enumerate(words):
        if word == "light" and i + 1 < len(words) and words[i + 1].isdigit():
            light_count = int(words[i + 1])
        elif word == "dark" and i + 1 < len(words) and words[i + 1].isdigit():
            dark_count = int(words[i + 1])

    return light_count, dark_count


def _parse_input(options_list: List[dict]) -> Union[List[int], Tuple[str, int, int]]:
    """Parse input option and return (light_count, dark_count) or digits list."""
    input_text = ""
    for opt in options_list or []:
        if opt.get("name") == "input":
            value = opt.get("value")
            if isinstance(value, str):
                input_text = value
            else:
                input_text = str(value)
            break

    if not input_text:
        return []

    # Check for light/dark keywords using the new parser
    light_dark_result = _parse_light_dark_input(input_text)
    if light_dark_result and (light_dark_result[0] > 0 or light_dark_result[1] > 0):
        return ("light_dark", light_dark_result[0], light_dark_result[1])

    # Fallback: extract digits only (original behavior)
    return [int(d) for d in re.findall(r"\d", input_text)]


async def _roll_command(interaction: Any) -> Any:
    """Handle the generic /roll command using a single text input option."""
    options = (
        interaction.data.options
        if hasattr(interaction.data, "options") and interaction.data.options is not None
        else []
    )

    # Check for separate light/dark parameters first
    light_count = None
    dark_count = None

    for opt in options:
        if opt.get("name") == "light":
            light_count = opt.get("value", 0)
        elif opt.get("name") == "dark":
            dark_count = opt.get("value", 0)

    # If we have light or dark parameters, use light/dark logic
    if light_count is not None or dark_count is not None:
        light_count = light_count if light_count is not None else 0
        dark_count = dark_count if dark_count is not None else 0
        return await _handle_light_dark_roll(interaction, light_count, dark_count)

    # Otherwise, parse the input parameter
    parsed = _parse_input(options)

    # Check if it's light/dark format from input string
    if isinstance(parsed, tuple) and len(parsed) == 3 and parsed[0] == "light_dark":
        return await _handle_light_dark_roll(interaction, parsed[1], parsed[2])

    # Otherwise, it's the original digits-only format
    digits = parsed if isinstance(parsed, list) else []

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
