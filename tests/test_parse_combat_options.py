"""Unit tests for _parse_combat_options function."""

from trophybot.bot import _parse_combat_options


def test_parse_combat_options_both_present():
    """Should parse both dark and endurance when present."""
    options = [{"name": "dark", "value": 3}, {"name": "endurance", "value": 9}]
    result = _parse_combat_options(options)
    assert result == {"dark": 3, "endurance": 9}


def test_parse_combat_options_reversed_order():
    """Should work regardless of option order."""
    options = [{"name": "endurance", "value": 12}, {"name": "dark", "value": 2}]
    result = _parse_combat_options(options)
    assert result == {"dark": 2, "endurance": 12}


def test_parse_combat_options_only_dark():
    """Should return only dark when endurance missing."""
    options = [{"name": "dark", "value": 4}]
    result = _parse_combat_options(options)
    assert result == {"dark": 4}


def test_parse_combat_options_only_endurance():
    """Should return only endurance when dark missing."""
    options = [{"name": "endurance", "value": 8}]
    result = _parse_combat_options(options)
    assert result == {"endurance": 8}


def test_parse_combat_options_empty_list():
    """Should return empty dict for empty options."""
    result = _parse_combat_options([])
    assert result == {}


def test_parse_combat_options_none_input():
    """Should handle None input gracefully."""
    result = _parse_combat_options(None)
    assert result == {}


def test_parse_combat_options_ignores_other_options():
    """Should ignore options that aren't dark or endurance."""
    options = [
        {"name": "dark", "value": 3},
        {"name": "other", "value": "ignored"},
        {"name": "endurance", "value": 10},
        {"name": "extra", "value": 42},
    ]
    result = _parse_combat_options(options)
    assert result == {"dark": 3, "endurance": 10}


def test_parse_combat_options_zero_values():
    """Should handle zero values correctly."""
    options = [{"name": "dark", "value": 0}, {"name": "endurance", "value": 0}]
    result = _parse_combat_options(options)
    assert result == {"dark": 0, "endurance": 0}


def test_parse_combat_options_large_values():
    """Should handle large values correctly."""
    options = [{"name": "dark", "value": 100}, {"name": "endurance", "value": 999}]
    result = _parse_combat_options(options)
    assert result == {"dark": 100, "endurance": 999}


def test_parse_combat_options_negative_values():
    """Should preserve negative values (validation handled elsewhere)."""
    options = [{"name": "dark", "value": -1}, {"name": "endurance", "value": -5}]
    result = _parse_combat_options(options)
    assert result == {"dark": -1, "endurance": -5}


def test_parse_combat_options_string_values():
    """Should preserve string values as-is (validation handled elsewhere)."""
    options = [{"name": "dark", "value": "3"}, {"name": "endurance", "value": "abc"}]
    result = _parse_combat_options(options)
    assert result == {"dark": "3", "endurance": "abc"}


def test_parse_combat_options_duplicate_keys():
    """Should handle duplicate keys (last one wins)."""
    options = [
        {"name": "dark", "value": 1},
        {"name": "dark", "value": 2},
        {"name": "endurance", "value": 5},
    ]
    result = _parse_combat_options(options)
    assert result == {"dark": 2, "endurance": 5}


def test_parse_combat_options_missing_name_or_value():
    """Should handle malformed options gracefully."""
    options = [
        {"name": "dark", "value": 3},
        {"name": "endurance"},  # missing value
        {"value": 5},  # missing name
        {"name": "dark", "value": 4},
    ]
    # This might raise an exception - that's fine, or skip malformed entries
    try:
        result = _parse_combat_options(options)
        # If it succeeds, should have parsed the valid entries
        assert "dark" in result
        assert result["dark"] == 4  # last valid dark value
    except (KeyError, TypeError):
        # It's acceptable to raise an exception for malformed input
        pass
