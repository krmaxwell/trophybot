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
  - if issued as `/roll [light]` (e.g. `/roll 2`), it rolls that many light-type d6s and reports the highest
  - if issued as `/roll [light] [dark]` (e.g. `/roll 2 3`), it rolls that many light-type and dark-type d6s, highlights the highest die and whether it was dark

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
