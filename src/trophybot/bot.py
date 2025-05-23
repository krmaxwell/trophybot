import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from trophybot.dice import roll_d6

intents = discord.Intents.default()
bot = commands.Bot(command_prefix=None, intents=intents)


@bot.event
async def on_ready():
    """Sync slash commands when the bot is ready."""
    await bot.tree.sync()
    print(f"Logged in as {bot.user}. Slash commands synced.")


@bot.tree.command(name="roll_d6", description="Rolls a six-sided die.")
async def roll_d6_command(interaction: discord.Interaction):
    """Roll a six-sided die and send the result."""
    result = roll_d6()
    await interaction.response.send_message(f"🎲 You rolled: {result}")


def main():
    """Load environment and run the Discord bot."""
    load_dotenv()
    try:
        token = os.environ["DISCORD_TOKEN"]
    except KeyError:
        raise RuntimeError("DISCORD_TOKEN environment variable not set") from None
    bot.run(token)


if __name__ == "__main__":
    main()
