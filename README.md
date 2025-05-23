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

Use the following slash commands in Discord:

- `/roll_d6`: Roll a six-sided die and return the result.

## Google Cloud Functions Deployment

You can deploy this project as a stateless Google Cloud Function to handle Discord slash commands without running a persistent bot.

### Deployment

1. Deploy using the `gcloud` CLI, specifying your Discord application's **public key**:

   ```sh
   gcloud functions deploy trophybot \
     --runtime python310 \
     --trigger-http \
     --allow-unauthenticated \
     --entry-point trophybot \
     --set-env-vars DISCORD_PUBLIC_KEY=YOUR_DISCORD_PUBLIC_KEY
   ```

   The `main.py` in the project root exports the `trophybot` function handler.

2. (Optional) If you update the public key or redeploy, run the same `gcloud functions deploy` command with the updated key.

This function verifies request signatures, responds to ping events, and handles the `/roll_d6` command.
