#!/usr/bin/env python3
import os
import subprocess
import sys

import requests
from dotenv import load_dotenv

# Required env vars
APP_ID = os.environ.get("DISCORD_APP_ID")
BOT_TOKEN = os.environ.get("DISCORD_TOKEN")
GCP_PROJECT = os.environ.get("GCP_PROJECT")
GCP_REGION = os.environ.get("GCP_REGION", "us-central1")
TEST_GUILD_ID = os.environ.get("TEST_GUILD_ID")  # optional for guild-scoped commands

if not APP_ID or not BOT_TOKEN or not GCP_PROJECT:
    print(
        "Error: DISCORD_APP_ID, DISCORD_TOKEN, and GCP_PROJECT must be set in .env",
        file=sys.stderr,
    )
    sys.exit(1)

BASE_URL = "https://discord.com/api/v10"
HEADERS = {"Authorization": f"Bot {BOT_TOKEN}", "Content-Type": "application/json"}

# Define your slash commands here
COMMANDS = [
    {
        "name": "roll",
        "description": "Roll a six-sided die or pool",
        "options": [
            {
                "name": "light",
                "description": "Number of light dice (default 1)",
                "type": 4,  # INTEGER
                "required": False,
            },
            {
                "name": "dark",
                "description": "Number of dark dice (default 0)",
                "type": 4,  # INTEGER
                "required": False,
            },
        ],
    },
    {
        "name": "combat",
        "description": "Trophy Gold endurance test",
        "options": [
            {
                "name": "dark",
                "description": "Number of dark dice",
                "type": 4,
                "required": True,
            },
            {
                "name": "endurance",
                "description": "Monster endurance value",
                "type": 4,
                "required": True,
            },
        ],
    },
    {
        "name": "gold",
        "description": "Trophy Gold loot roll",
        "options": [
            {
                "name": "count",
                "description": "Number of gold dice to roll",
                "type": 4,
                "required": True,
            }
        ],
    },
]


def register_commands():
    """Register slash commands with Discord API."""
    if TEST_GUILD_ID:
        url = f"{BASE_URL}/applications/{APP_ID}/guilds/{TEST_GUILD_ID}/commands"
        scope = f"guild {TEST_GUILD_ID}"
    else:
        url = f"{BASE_URL}/applications/{APP_ID}/commands"
        scope = "global"
    print(f"Registering commands ({scope}):")
    failures = []
    for cmd in COMMANDS:
        try:
            resp = requests.post(url, headers=HEADERS, json=cmd)
            if resp.status_code in (200, 201):
                print(f"  ✓ {cmd['name']}")
            else:
                error_message = f"{resp.status_code}: {resp.text}"
                failures.append((cmd["name"], error_message))
                print(f"  ✗ {cmd['name']} -> {error_message}")
        except Exception as e:
            error_message = str(e)
            failures.append((cmd["name"], error_message))
            print(f"  ✗ {cmd['name']} -> Exception: {error_message}")
    if failures:
        print("Command registration encountered errors:", file=sys.stderr)
        for name, err in failures:
            print(f" - {name}: {err}", file=sys.stderr)
        sys.exit(1)


def deploy_cloud_run():
    """Deploy the container to Google Cloud Run."""
    deploy_cmd = [
        "gcloud",
        "run",
        "deploy",
        "trophybot",
        "--source",
        ".",
        "--project",
        GCP_PROJECT,
        "--region",
        GCP_REGION,
        "--allow-unauthenticated",
        "--update-secrets",
        "DISCORD_TOKEN=discord-token:latest",
        "--update-secrets",
        "DISCORD_PUBLIC_KEY=discord-pubkey:latest",
    ]
    print("Deploying to Cloud Run:")
    print(" ".join(deploy_cmd))
    subprocess.run(deploy_cmd, check=True)


def main():
    """
    Load local environment variables if in development, register Discord commands,
    and deploy to Cloud Run.
    """
    if os.environ.get("ENV", "dev") == "dev":
        load_dotenv()
    register_commands()
    deploy_cloud_run()


if __name__ == "__main__":
    main()
