"""File này tạo dữ liệu mẫu cho chương trình.

Dữ liệu có thể là random, đã sắp xếp tăng dần hoặc sắp xếp giảm dần.
"""

from __future__ import annotations

import random
from typing import List


def generate_random(n: int, low: int = 1, high: int = 1000) -> List[int]:
    """Tạo một mảng số nguyên ngẫu nhiên.
    
    Args:
        n: Số phần tử cần tạo.
        low: Giá trị nhỏ nhất có thể có.
        high: Giá trị lớn nhất có thể có.
    
    Return:
        Một mảng số nguyên random.
    """
    if n <= 0:
        raise ValueError(f"n must be positive, got {n}")
    return [random.randint(low, high) for _ in range(n)]


def generate_sorted(n: int, low: int = 1, high: int = 1000) -> List[int]:
    """Tạo một mảng đã sắp xếp tăng dần.
    
    Args:
        n: Số phần tử cần tạo.
        low: Giá trị nhỏ nhất có thể có.
        high: Giá trị lớn nhất có thể có.
    
    Return:
        Một mảng số nguyên đã sắp xếp tăng dần.
    """
    if n <= 0:
        raise ValueError(f"n must be positive, got {n}")
    data = generate_random(n, low, high)
    data.sort()
    return data


def generate_reversed(n: int, low: int = 1, high: int = 1000) -> List[int]:
    """Tạo một mảng đã sắp xếp giảm dần.
    
    Args:
        n: Số phần tử cần tạo.
        low: Giá trị nhỏ nhất có thể có.
        high: Giá trị lớn nhất có thể có.
    
    Return:
        Một mảng số nguyên đã sắp xếp giảm dần.
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
    """Tạo mảng theo kiểu được chọn.
    
    Args:
        n: Số phần tử cần tạo.
        input_type: Kiểu mảng, gồm ``Random``, ``Sorted`` hoặc ``Reversed``.
        low: Giá trị nhỏ nhất có thể có.
        high: Giá trị lớn nhất có thể có.
    
    Return:
        Một mảng số nguyên theo đúng kiểu được chọn.
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
