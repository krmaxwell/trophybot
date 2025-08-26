"""Unit tests for _parse_light_dark_input function."""

from trophybot.bot import _parse_light_dark_input


def test_parse_light_dark_basic():
    """Should parse basic light X dark Y format."""
    result = _parse_light_dark_input("light 3 dark 2")
    assert result == (3, 2)


def test_parse_dark_light_reversed():
    """Should parse dark Y light X format."""
    result = _parse_light_dark_input("dark 2 light 3")
    assert result == (3, 2)


def test_parse_only_light():
    """Should parse light-only input."""
    result = _parse_light_dark_input("light 5")
    assert result == (5, 0)


def test_parse_only_dark():
    """Should parse dark-only input."""
    result = _parse_light_dark_input("dark 4")
    assert result == (0, 4)


def test_parse_case_insensitive():
    """Should be case insensitive."""
    result = _parse_light_dark_input("LIGHT 2 DARK 1")
    assert result == (2, 1)

    result = _parse_light_dark_input("Light 3 Dark 4")
    assert result == (3, 4)


def test_parse_rejects_ambiguous_patterns():
    """Should reject ambiguous patterns that don't match valid formats."""
    # These should all return (0, 0) as they don't match valid patterns:
    # Valid: "N", "light N", "dark N", "light M dark N", "dark M light N"

    # Numbers before keywords - ambiguous
    assert _parse_light_dark_input("3 light 2 dark") == (0, 0)
    assert _parse_light_dark_input("5 light") == (0, 0)
    assert _parse_light_dark_input("2 dark") == (0, 0)

    # Extra words mixed in - not valid patterns
    assert _parse_light_dark_input("roll light 2 and dark 3 dice") == (0, 0)
    assert _parse_light_dark_input("please light 3") == (0, 0)
    assert _parse_light_dark_input("dark 2 now") == (0, 0)

    # Multiple numbers with single keyword
    assert _parse_light_dark_input("light 2 3") == (0, 0)
    assert _parse_light_dark_input("dark 1 4 5") == (0, 0)

    # Keywords without proper numbers
    assert _parse_light_dark_input("light abc") == (0, 0)
    assert _parse_light_dark_input("dark xyz light 3") == (0, 0)


def test_parse_empty_string():
    """Should return (0, 0) for empty string."""
    result = _parse_light_dark_input("")
    assert result == (0, 0)


def test_parse_no_keywords():
    """Should return (0, 0) when no light/dark keywords found."""
    result = _parse_light_dark_input("roll 3 dice")
    assert result == (0, 0)


def test_parse_keywords_without_numbers():
    """Should return (0, 0) when keywords present but no valid numbers."""
    result = _parse_light_dark_input("light dark")
    assert result == (0, 0)

    result = _parse_light_dark_input("light abc dark xyz")
    assert result == (0, 0)


def test_parse_number_before_keyword():
    """Should not parse numbers that come before keywords."""
    result = _parse_light_dark_input("3 light 2 dark")
    assert result == (0, 0)


def test_parse_multiple_light_dark():
    """Should reject input with multiple light/dark keywords as ambiguous."""
    result = _parse_light_dark_input("light 1 dark 2 light 3 dark 4")
    assert result == (0, 0)  # Ambiguous input should be rejected


def test_parse_large_numbers():
    """Should handle large numbers correctly."""
    result = _parse_light_dark_input("light 99 dark 100")
    assert result == (99, 100)


def test_parse_zero_values():
    """Should handle zero values."""
    result = _parse_light_dark_input("light 0 dark 0")
    assert result == (0, 0)


def test_parse_whitespace_variations():
    """Should handle various whitespace patterns for valid formats only."""
    result = _parse_light_dark_input("  light   3   dark   2  ")
    assert result == (3, 2)

    result = _parse_light_dark_input("light  5")
    assert result == (5, 0)

    result = _parse_light_dark_input("  dark  3  ")
    assert result == (0, 3)


def test_parse_valid_patterns_comprehensive():
    """Test all valid patterns are accepted correctly."""
    # Valid pattern: "light N"
    assert _parse_light_dark_input("light 1") == (1, 0)
    assert _parse_light_dark_input("light 10") == (10, 0)

    # Valid pattern: "dark N"
    assert _parse_light_dark_input("dark 2") == (0, 2)
    assert _parse_light_dark_input("dark 15") == (0, 15)

    # Valid pattern: "light M dark N"
    assert _parse_light_dark_input("light 3 dark 4") == (3, 4)
    assert _parse_light_dark_input("light 0 dark 1") == (0, 1)

    # Valid pattern: "dark M light N"
    assert _parse_light_dark_input("dark 5 light 6") == (6, 5)
    assert _parse_light_dark_input("dark 1 light 0") == (0, 1)


def test_parse_strict_format_enforcement():
    """Test that only exact valid formats are accepted."""
    # These should work (exact matches of valid patterns)
    assert _parse_light_dark_input("light 3") == (3, 0)
    assert _parse_light_dark_input("dark 2 light 1") == (1, 2)

    # These should fail (not exact matches)
    assert _parse_light_dark_input("light") == (0, 0)  # missing number
    assert _parse_light_dark_input("3") == (0, 0)  # bare number (handled by fallback)
    assert _parse_light_dark_input("light 3 dice") == (0, 0)  # extra word
    assert _parse_light_dark_input("roll light 3 dark 2") == (0, 0)  # extra word


def test_parse_none_input_handles_gracefully():
    """Should handle None input gracefully without crashing."""
    # Function should not crash on invalid input
    try:
        result = _parse_light_dark_input(None)
        # If it returns something, should be (0, 0) for no valid parse
        assert result == (0, 0)
    except (AttributeError, TypeError):
        # Or it should handle the error gracefully
        pass
