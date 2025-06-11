"""
Roll dice for the Trophy RPG system.

This module provides functions to roll a single d6 and a pool of d6s.
"""

import secrets
from typing import List


def roll_d6() -> int:
    """Roll a six-sided die."""
    return secrets.randbelow(6) + 1


# Alias for roll_d6
roll = roll_d6


def roll_pool(n: int) -> List[int]:
    """
    Roll a pool of ``n`` six-sided dice.

    Raises ``ValueError`` if ``n`` is negative.
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    return [roll_d6() for _ in range(n)]
