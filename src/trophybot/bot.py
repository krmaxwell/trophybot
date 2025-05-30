from trophybot.dice import roll_d6

# Expose roll function for testing and aliasing
roll = roll_d6


class _Command:
    def __init__(self, callback):
        self.callback = callback


async def _roll_command(interaction):
    """Roll a d6 or pool as the generic /roll command."""
    result = roll()
    await interaction.response.send_message(f"🎲 You rolled: {result}")


roll_command = _Command(_roll_command)
