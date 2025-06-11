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

- `/roll [input]`
  - `input` is optional text that may contain zero, one, or two digits
  - with no digits (plain `/roll`), a single die is rolled and the result reported
  - with one digit (e.g. `/roll 3`), that many dice are rolled, all results are listed, and the highest die is noted
  - with two digits (e.g. `/roll 2 3`), two pools are rolled – the first is "light" and the second "dark" – and the highest die and its colour are reported (dark wins any ties)

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

This deploys `main.py` as an HTTP endpoint on Cloud Run, verifying request signatures and handling `/roll` commands.
