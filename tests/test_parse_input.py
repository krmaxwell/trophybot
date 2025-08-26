"""Unit tests for _parse_input function."""

from trophybot.bot import _parse_input


def test_parse_input_empty_options():
    """Should return empty list when no options provided."""
    assert _parse_input([]) == []
    assert _parse_input(None) == []


def test_parse_input_no_input_option():
    """Should return empty list when input option is missing."""
    options = [{"name": "other", "value": "test"}]
    assert _parse_input(options) == []


def test_parse_input_empty_string():
    """Should return empty list when input is empty string."""
    options = [{"name": "input", "value": ""}]
    assert _parse_input(options) == []


def test_parse_input_light_dark_format():
    """Should parse light/dark format and return tuple."""
    options = [{"name": "input", "value": "light 3 dark 2"}]
    result = _parse_input(options)
    assert result == ("light_dark", 3, 2)


def test_parse_input_only_light():
    """Should parse light-only format."""
    options = [{"name": "input", "value": "light 4"}]
    result = _parse_input(options)
    assert result == ("light_dark", 4, 0)


def test_parse_input_only_dark():
    """Should parse dark-only format."""
    options = [{"name": "input", "value": "dark 2"}]
    result = _parse_input(options)
    assert result == ("light_dark", 0, 2)


def test_parse_input_digit_fallback():
    """Should extract digits when not light/dark format."""
    options = [{"name": "input", "value": "3 5"}]
    result = _parse_input(options)
    assert result == [3, 5]


def test_parse_input_single_digit():
    """Should extract single digit."""
    options = [{"name": "input", "value": "4"}]
    result = _parse_input(options)
    assert result == [4]


def test_parse_input_mixed_text_digits():
    """Should extract only digits from mixed text."""
    options = [{"name": "input", "value": "roll 2 dice now 6"}]
    result = _parse_input(options)
    assert result == [2, 6]


def test_parse_input_non_string_value():
    """Should handle non-string values by converting to string."""
    options = [{"name": "input", "value": 123}]
    result = _parse_input(options)
    assert result == [1, 2, 3]


def test_parse_input_case_insensitive_light_dark():
    """Should handle case variations in light/dark format."""
    options = [{"name": "input", "value": "Light 2 Dark 3"}]
    result = _parse_input(options)
    assert result == ("light_dark", 2, 3)


def test_parse_input_reversed_dark_light():
    """Should handle dark/light in any order."""
    options = [{"name": "input", "value": "dark 1 light 4"}]
    result = _parse_input(options)
    assert result == ("light_dark", 4, 1)
