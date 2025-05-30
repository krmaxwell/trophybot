from trophybot.dice import roll_d6


class _Command:
    def __init__(self, callback):
        self.callback = callback


async def _roll_d6_command(interaction):
    """Roll a six-sided die and send the result."""
    result = roll_d6()
    await interaction.response.send_message(f"🎲 You rolled: {result}")


roll_d6_command = _Command(_roll_d6_command)
