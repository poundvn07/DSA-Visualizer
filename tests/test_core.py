#!/usr/bin/env python3
"""Quick smoke test for all core modules."""

import sys
import os

# Ensure project root is on the path.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.step import Step
from src.core.algorithms import (
    quick_sort_gen, heap_sort_gen, merge_sort_gen, binary_search_gen,
    quick_sort_plain, heap_sort_plain, merge_sort_plain,
)
from src.core.pseudocode import get_pseudocode, PSEUDOCODE
from src.benchmarking.data_generator import generate_array
from src.utils.helpers import scale_values, clamp, format_ms


def main():
    print("=== Step dataclass ===")
    s = Step(type="compare", indices=[0, 1], array_state=[3, 1],
             description="test", highlight_line=0)
    print(f"  OK: {s.type} {s.indices}")

    print("\n=== Algorithms (generators) ===")
    arr = [5, 3, 8, 1, 4]
    for name, gen in [("QuickSort", quick_sort_gen),
                      ("HeapSort", heap_sort_gen),
                      ("MergeSort", merge_sort_gen)]:
        steps = list(gen(list(arr)))
        final = steps[-1].array_state
        assert final == sorted(arr), f"{name} final: {final}"
        print(f"  {name}: {len(steps)} steps → {final}")

    print("\n=== Binary Search ===")
    sorted_arr = [1, 3, 4, 5, 8]
    steps = list(binary_search_gen(sorted_arr, 4))
    print(f"  Steps: {len(steps)}, Last: {steps[-1].type} - {steps[-1].description}")
    assert steps[-1].type == "found"

    steps2 = list(binary_search_gen(sorted_arr, 99))
    print(f"  Not found: {steps2[-1].type} - {steps2[-1].description}")
    assert steps2[-1].type == "not_found"

    print("\n=== Pseudocode ===")
    for algo_name in PSEUDOCODE:
        lines = get_pseudocode(algo_name)
        print(f"  {algo_name}: {len(lines)} lines")

    print("\n=== Data Generator ===")
    for t in ("Random", "Sorted", "Reversed"):
        a = generate_array(10, t)
        print(f"  {t}: {a}")

    print("\n=== Plain sorts (benchmark variants) ===")
    for name, fn in [("QuickSort", quick_sort_plain),
                     ("HeapSort", heap_sort_plain),
                     ("MergeSort", merge_sort_plain)]:
        data = list(arr)
        result = fn(data)
        assert result == sorted(arr), f"{name} plain: {result}"
        print(f"  {name}: {result}")

    print("\n=== Helpers ===")
    print(f"  clamp(150, 0, 100) = {clamp(150, 0, 100)}")
    print(f"  scale_values([1,5,10], 100) = {scale_values([1, 5, 10], 100.0)}")
    print(f"  format_ms(1234.5) = {format_ms(1234.5)}")

    print("\n✅ All tests passed!")


if __name__ == "__main__":
    main()
