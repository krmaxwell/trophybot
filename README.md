# trophybot

trophybot is a Discord dice roller for the Trophy RPG.

## Setup

1. Create a `.env` file in the project root and set your Discord bot token:

   ```sh
   DISCORD_TOKEN=your_discord_bot_token_here
   ```

2. Install dependencies:

   ```sh
   poetry install
   ```

3. Run the bot:

   ```sh
   # via Poetry script
   poetry run trophybot

   # or directly
   python -m trophybot
   ```

## Commands

- `!roll_d6`: Roll a six-sided die and return the result.
