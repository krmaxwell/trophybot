import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from trophybot.dice import roll_d6

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN is None:
    raise RuntimeError("DISCORD_TOKEN environment variable not set")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.command(name="roll_d6", help="Rolls a six-sided die.")
async def roll_d6_command(ctx):
    """Roll a six-sided die and send the result."""
    result = roll_d6()
    await ctx.send(f"🎲 You rolled: {result}")


def main():
    """Run the Discord bot."""
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
