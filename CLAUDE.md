# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

trophybot is a Discord dice roller bot for the Trophy RPG system. It's deployed as a Flask web service that handles Discord slash commands via HTTP interactions.

## Common Commands

### Development
- **Install dependencies**: `poetry install`
- **Run locally**: `python main.py` (runs Flask server on port 8080)
- **Run tests**: `pytest`
- **Run tests with coverage**: `coverage run -m pytest && coverage report`
- **Lint code**: `ruff check .`
- **Format code**: `ruff format .`
- **Type check**: `mypy .`

### Deployment
- **Deploy to Google Cloud Run**: `gcloud run deploy trophybot --source . --allow-unauthenticated --region YOUR_REGION --set-env-vars DISCORD_PUBLIC_KEY=your_key --port 8080`

## Architecture

### Core Components

1. **main.py**: Flask application entry point that:
   - Handles Discord interaction verification using Ed25519 signatures
   - Routes Discord slash commands to appropriate handlers
   - Implements async command processing with fake interaction objects

2. **src/trophybot/bot.py**: Command handlers that implement Trophy RPG dice mechanics:
   - `/roll` command with flexible input parsing (0, 1, or 2 digit parameters)
   - `/combat` command for endurance tests with dark dice pools
   - Uses a custom `_Command` wrapper class for async callbacks

3. **src/trophybot/dice.py**: Core dice rolling engine:
   - Uses `secrets.randbelow()` for cryptographically secure randomness
   - Provides `roll_d6()` and `roll_pool(n)` functions

### Key Patterns

- **Async command handling**: Commands are async functions that return Discord interaction responses
- **Option parsing**: Discord slash command options are parsed from nested JSON structures
- **Fake interaction pattern**: Uses `SimpleNamespace` objects to simulate Discord.py interaction objects for testing/compatibility
- **Dice mechanics**: Implements Trophy RPG's light/dark dice system with proper tie-breaking (dark wins ties)

### Environment Setup

- Requires `DISCORD_PUBLIC_KEY` environment variable for request verification
- Uses `.env` file for local development
- Flask runs on port 8080 by default (configurable via `PORT` env var)

### Testing

- Uses pytest with `pytest-asyncio` for async test support
- Tests cover dice mechanics, command parsing, and interaction handling
- Configuration in `pytest.ini` disables anyio plugin

### Code Quality

- **Linting/Formatting**: Ruff with 88-character line length
- **Type checking**: MyPy enabled
- **Pre-commit hooks**: Available for automated quality checks
- **Security**: Uses PyNaCl for Discord signature verification