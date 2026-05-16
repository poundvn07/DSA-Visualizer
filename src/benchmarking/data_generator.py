"""Data generator for benchmarking and visualization.

Provides factory functions that create integer arrays of various
distributions (random, sorted, reversed) used both by the GUI's
configuration panel and by the benchmark runner.
"""

from __future__ import annotations

import random
from typing import List


def generate_random(n: int, low: int = 1, high: int = 1000) -> List[int]:
    """Generate a list of *n* uniformly random integers.

    Args:
        n: Number of elements.
        low: Lower bound (inclusive) for each element.
        high: Upper bound (inclusive) for each element.

    Returns:
        A new ``list[int]`` of length *n*.

    Raises:
        ValueError: If *n* is non-positive.
    """
    if n <= 0:
        raise ValueError(f"n must be positive, got {n}")
    return [random.randint(low, high) for _ in range(n)]


def generate_sorted(n: int, low: int = 1, high: int = 1000) -> List[int]:
    """Generate a sorted list of *n* integers.

    Args:
        n: Number of elements.
        low: Lower bound (inclusive).
        high: Upper bound (inclusive).

    Returns:
        A sorted ``list[int]`` of length *n*.

    Raises:
        ValueError: If *n* is non-positive.
    """
    if n <= 0:
        raise ValueError(f"n must be positive, got {n}")
    data = generate_random(n, low, high)
    data.sort()
    return data


def generate_reversed(n: int, low: int = 1, high: int = 1000) -> List[int]:
    """Generate a reverse-sorted list of *n* integers.

    Args:
        n: Number of elements.
        low: Lower bound (inclusive).
        high: Upper bound (inclusive).

    Returns:
        A reverse-sorted ``list[int]`` of length *n*.

    Raises:
        ValueError: If *n* is non-positive.
    """
    if n <= 0:
        raise ValueError(f"n must be positive, got {n}")
    data = generate_random(n, low, high)
    data.sort(reverse=True)
    return data


def generate_array(
    n: int,
    input_type: str = "Random",
    low: int = 1,
    high: int = 1000,
) -> List[int]:
    """Dispatch to the appropriate generator based on *input_type*.

    Args:
        n: Number of elements.
        input_type: One of ``"Random"``, ``"Sorted"``, or ``"Reversed"``.
        low: Lower bound (inclusive).
        high: Upper bound (inclusive).

    Returns:
        A ``list[int]`` of the requested distribution.

    Raises:
        ValueError: If *input_type* is not recognised.
    """
    factories = {
        "Random": generate_random,
        "Sorted": generate_sorted,
        "Reversed": generate_reversed,
    }
    factory = factories.get(input_type)
    if factory is None:
        raise ValueError(
            f"Unknown input_type {input_type!r}. "
            f"Expected one of {list(factories.keys())}"
        )
    return factory(n, low, high)
