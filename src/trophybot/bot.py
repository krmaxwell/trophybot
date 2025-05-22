import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from trophybot.dice import roll_d6

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.command(name="roll_d6", help="Rolls a six-sided die.")
async def roll_d6_command(ctx):
    """Roll a six-sided die and send the result."""
    result = roll_d6()
    await ctx.send(f"🎲 You rolled: {result}")


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
