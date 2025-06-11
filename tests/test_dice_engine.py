import pytest

from trophybot.dice import roll_d6, roll_pool


def test_roll_d6_range():
    for _ in range(100):
        assert 1 <= roll_d6() <= 6


def test_roll_pool_length():
    pool = roll_pool(3)
    assert len(pool) == 3


def test_roll_pool_range():
    pool = roll_pool(2)
    assert 1 <= pool[0] <= 6
    assert 1 <= pool[1] <= 6


def test_roll_pool_negative():
    with pytest.raises(ValueError):
        roll_pool(-1)
