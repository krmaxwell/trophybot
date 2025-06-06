# trophybot

trophybot is a Discord dice roller for the Trophy RPG.

## Setup

1. Create a `.env` file in the project root and set your Discord application's public key:

   ```sh
   DISCORD_PUBLIC_KEY=your_discord_public_key_here
   ```

2. Install dependencies:

   ```sh
   poetry install
   ```

3. Run the server locally:

   ```sh
   python main.py
   ```

## Commands

Use the following slash commands in Discord:

- `/roll [light] [dark]`
  - if issued just as `/roll`, it rolls one d6 and reports the result
  - if issued as `/roll [light]` (e.g. `/roll 2`), it rolls that many light-type d6s and reports all dice rolls, then indicates the highest
  - if issued as `/roll [dark]` (e.g. `/roll 3`), it rolls that many dark-type d6s and reports all dice rolls, then indicates the highest
  - if issued as `/roll [light] [dark]` (e.g. `/roll light=2 dark=3`), it rolls that many light-type and dark-type d6s, shows all results grouped by color, and indicates the highest die and its color (e.g., "Light 1 5 Dark 3 4 6 => Dark 6 is highest"). Per the rules, if there is a tie between the highest light and dark dice, the dark die wins

## Cloud Run Deployment

You can deploy this project as a containerized service on Google Cloud Run to handle Discord interactions via HTTP.

### Deployment

```sh
gcloud run deploy trophybot \
  --source . \
  --allow-unauthenticated \
  --region YOUR_REGION \
  --set-env-vars DISCORD_PUBLIC_KEY=your_discord_public_key_here \
  --port 8080
```

This deploys `main.py` as an HTTP endpoint on Cloud Run, verifying request signatures and handling `/roll_d6` commands.
