#!/usr/bin/env python3
"""File này test nhanh một vài tính năng của thuật toán.

Nó kiểm tra pivot của QuickSort, mô tả bước và việc đổi Step sang JSON.
"""
from src.core.algorithms import quick_sort_gen, heap_sort_gen, merge_sort_gen, binary_search_gen
from dataclasses import asdict
import json

# Feature 7: pivot strategies
for strat in ["last", "first", "middle", "median3"]:
    steps = list(quick_sort_gen([5, 3, 8, 1, 9], pivot_strategy=strat))
    print(f"QS ({strat:>8}): {len(steps):>3} steps | {steps[0].description}")

# Feature 9: enriched descriptions
hs = list(heap_sort_gen([5, 3, 8, 1]))
print(f"\nHeapSort: {len(hs)} steps | {hs[0].description}")

ms = list(merge_sort_gen([5, 3, 8, 1]))
print(f"MergeSort: {len(ms)} steps | {ms[0].description}")

bs = list(binary_search_gen([1, 3, 5, 7, 9], 5))
print(f"BinarySearch: {len(bs)} steps | last: {bs[-1].description}")

# JSON serialization
d = asdict(hs[0])
json.dumps(d)
print("\nAll tests passed!")
