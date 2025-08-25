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
- All commits must pass Ruff

## Development Guidelines

### Test-Driven Development (TDD)

Follow proper TDD practices when implementing new features:

1. **Write failing tests first**: Tests should demonstrate the expected behavior and fail initially
2. **Write minimal code to pass**: Implement just enough code to make the tests pass
3. **Refactor with confidence**: Improve code while keeping tests green
4. **Never write tests that pass for broken behavior**: Avoid tests with commented assertions or tests that assert incorrect behavior

**Example of good TDD practice:**
```python
def test_roll_light_3_should_use_light_dark_format():
    """Test that '/roll light 3' should show light/dark format."""
    # Test shows expected behavior and fails until implemented
    assert actual_response == "Light rolls: 1 4 2 => Highest Light 4"
```

**Avoid this anti-pattern:**
```python
def test_current_broken_behavior():
    # This test passes but validates incorrect behavior
    assert actual_response == "Dice rolls: 1 4 2 => Highest 4"
    # assert actual_response == "Light rolls: 1 4 2 => Highest Light 4"  # commented out
```

### Type Safety

Add type hints to all new functions for better maintainability:

1. **Use explicit type hints**: Import from `typing` module as needed
2. **Document complex return types**: Use `Union` for multiple return types
3. **Prefer specific types over `Any`**: Only use `Any` when dealing with external interfaces
4. **Use `Optional` for nullable returns**: Be explicit about functions that can return `None`

**Example of good type hints:**
```python
def _parse_input(options_list: List[dict]) -> Union[List[int], Tuple[str, int, int]]:
    """Parse input option and return (light_count, dark_count) or digits list."""

def _parse_light_dark_input(text: str) -> Optional[Tuple[int, int]]:
    """Parse 'light X dark Y' format in any order."""
```

**Type checking workflow:**
- Run `poetry run mypy .` to check type consistency
- External library type stubs may need to be installed (e.g., `types-requests`)
- MyPy errors about missing type stubs for external libraries can usually be ignored
- Focus on ensuring your new code has proper type annotations

### Refactoring Guidelines

When refactoring, prioritize:

1. **Maintainability**: Prefer simple, readable code over clever solutions
2. **Single Responsibility**: Functions should do one thing well
3. **Clear interfaces**: Use type hints and descriptive function names
4. **Avoid magic strings/numbers**: Use constants or enums for special values

**Example refactor - Replace complex regex with readable parsing:**
```python
# Before: Complex regex patterns
light_match = re.match(r"light\s+(\d+)", input_lower)
if light_match:
    return ("light_dark", int(light_match.group(1)), 0)

# After: Simple split and parse
def _parse_light_dark_input(text: str) -> Optional[Tuple[int, int]]:
    words = text.lower().split()
    # Clear, readable logic here
```