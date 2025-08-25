"""Tests for command registration functionality."""

import os
from unittest.mock import patch

import main


def test_no_automatic_command_registration_on_startup():
    """Test demonstrating the problem: commands not registered automatically."""

    # Mock the environment variables needed
    test_env = {
        "DISCORD_PUBLIC_KEY": "test_key",
        "DISCORD_APP_ID": "123456789",
        "DISCORD_TOKEN": "test_token",
        "GCP_PROJECT": "test-project",
    }

    with patch.dict(os.environ, test_env):
        with patch("requests.get") as mock_get:
            # Mock Discord API response showing no commands registered
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = []  # No commands registered

            # Import main module (simulating app startup)
            import importlib

            importlib.reload(main)

            # The problem: main.py doesn't register commands on startup
            # Commands should be registered automatically but they're not

            # Verify that no call was made to register commands
            # This test will currently PASS, showing the problem exists
            mock_get.assert_not_called()

            # This is what SHOULD happen (but doesn't):
            # - App should check if commands are registered on Discord
            # - If not, it should register them automatically
            # - But it doesn't, so commands must be registered manually via deploy.py


def test_commands_should_be_registered_automatically():
    """Test showing what SHOULD happen: automatic command registration on startup."""

    test_env = {
        "DISCORD_PUBLIC_KEY": "test_key",
        "DISCORD_APP_ID": "123456789",
        "DISCORD_TOKEN": "test_token",
        "GCP_PROJECT": "test-project",
    }

    with patch.dict(os.environ, test_env, clear=True):
        with (
            patch("main.requests.get") as mock_get,
            patch("main.requests.post") as mock_post,
        ):
            # Mock Discord API showing no commands currently registered
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = []

            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"id": "cmd_id"}

            # Call the registration function directly (simulating app startup)
            main._register_commands_if_needed()

            # Should check for existing commands
            expected_url = "https://discord.com/api/v10/applications/123456789/commands"
            expected_headers = {
                "Authorization": "Bot test_token",
                "Content-Type": "application/json",
            }
            mock_get.assert_called_once_with(
                expected_url, headers=expected_headers, timeout=30
            )

            # Should register the roll and combat commands
            assert mock_post.call_count == 2  # Two commands should be registered
