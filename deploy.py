#!/usr/bin/env python3
import json  # Added for parsing JSON responses
import os
import subprocess
import sys

import requests
from dotenv import load_dotenv

# Load .env file for local development if it exists.
# This ensures environment variables are loaded before they are accessed by the script.
load_dotenv()

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


def _fetch_existing_commands(url: str, headers: dict, scope_description: str) -> list:
    """Fetch existing slash commands from the Discord API for a given scope."""
    print(f"Fetching existing {scope_description} commands...")
    try:
        get_resp = requests.get(url, headers=headers)
        get_resp.raise_for_status()  # Raise an exception for HTTP errors
        existing_commands = get_resp.json()
        if not isinstance(existing_commands, list):
            print(
                f"  Error: Expected a list of commands, got {type(existing_commands)}",
                file=sys.stderr,
            )
            print(f"  Response: {existing_commands}", file=sys.stderr)
            sys.exit(1)
        print(f"  Found {len(existing_commands)} existing command(s).")
        if existing_commands:
            print("  Existing command names in this scope:")
            for cmd_data in existing_commands:
                print(f"    - {cmd_data.get('name')} (ID: {cmd_data.get('id')})")
        return existing_commands
    except requests.exceptions.RequestException as e:
        print(f"  Error fetching existing commands: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"  Error decoding existing commands JSON: {e}", file=sys.stderr)
        sys.exit(1)


def _delete_stale_commands(
    existing_commands: list,
    current_command_names: set,
    base_delete_url: str,
    headers: dict,
):
    """Delete stale commands from Discord."""
    commands_to_delete = [
        cmd for cmd in existing_commands if cmd.get("name") not in current_command_names
    ]

    if commands_to_delete:
        print(f"Deleting {len(commands_to_delete)} stale command(s)...")
        for cmd_to_delete in commands_to_delete:
            delete_url = f"{base_delete_url}/{cmd_to_delete['id']}"
            cmd_name = cmd_to_delete.get("name", "Unknown Command")
            cmd_id = cmd_to_delete.get("id", "Unknown ID")
            print(f"  Deleting '{cmd_name}' (ID: {cmd_id})...")
            try:
                del_resp = requests.delete(delete_url, headers=headers)
                if del_resp.status_code == 204:  # No Content on success
                    print(f"    ✓ Deleted '{cmd_name}'")
                else:
                    print(
                        f"    ✗ Error deleting '{cmd_name}': {del_resp.status_code} {del_resp.text}",  # noqa: E501
                        file=sys.stderr,
                    )
            except requests.exceptions.RequestException as e:
                print(
                    f"    ✗ Exception deleting '{cmd_name}': {e}",
                    file=sys.stderr,
                )


def _register_new_or_update_defined_commands(
    commands_to_register: list, registration_url: str, headers: dict
) -> list:
    """Register new commands or updates existing ones based on local definitions."""
    print(
        f"Registering/Updating {len(commands_to_register)} command(s) defined in deploy.py..."  # noqa: E501
    )
    failures = []
    for cmd_definition in commands_to_register:
        try:
            resp = requests.post(registration_url, headers=headers, json=cmd_definition)
            if resp.status_code in (200, 201):  # OK or Created
                print(f"  ✓ {cmd_definition['name']}")
            else:
                error_message = f"{resp.status_code}: {resp.text}"
                failures.append((cmd_definition["name"], error_message))
                print(f"  ✗ {cmd_definition['name']} -> {error_message}")
        except Exception as e:  # pylint: disable=broad-except
            error_message = str(e)
            failures.append((cmd_definition["name"], error_message))
            print(f"  ✗ {cmd_definition['name']} -> Exception: {error_message}")
    return failures


def register_commands():
    """
    Register slash commands with Discord API by fetching, deleting stale,
    and updating/creating.
    """
    if TEST_GUILD_ID:
        print("DEBUG: TEST_GUILD_ID =", TEST_GUILD_ID)
        url = f"{BASE_URL}/applications/{APP_ID}/guilds/{TEST_GUILD_ID}/commands"
        scope = f"guild {TEST_GUILD_ID}"
    else:
        print("DEBUG: No TEST_GUILD_ID found")
        url = f"{BASE_URL}/applications/{APP_ID}/commands"
        scope = "global"
    print(f"Registering commands ({scope}):")

    existing_commands = _fetch_existing_commands(url, HEADERS, scope)

    current_command_names = {cmd["name"] for cmd in COMMANDS}
    _delete_stale_commands(existing_commands, current_command_names, url, HEADERS)

    failures = _register_new_or_update_defined_commands(COMMANDS, url, HEADERS)

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
    register_commands()
    deploy_cloud_run()


if __name__ == "__main__":
    main()
