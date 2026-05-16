"""Eel-exposed Python functions — bridge between JS and src/core.

Every function decorated with ``@eel.expose`` becomes callable from
JavaScript via ``eel.<function_name>(args)()``.  This module is imported
by ``main.py`` purely for its side-effect of registering these functions
with the Eel runtime.

Design note:
    Python generators cannot be streamed directly to JS.  Instead, each
    ``get_*_steps`` function runs the generator to completion, collects
    every yielded :class:`Step` into a list of plain dicts (via
    ``dataclasses.asdict``), and returns the full list as JSON.
"""

from __future__ import annotations

import random
import threading
from dataclasses import asdict
from typing import Any, Dict, List, Optional

import eel

from src.benchmarking.benchmark_runner import BenchmarkRunner
from src.benchmarking.data_generator import generate_array as _generate_array
from src.core.algorithms import (
    binary_search_gen,
    heap_sort_gen,
    merge_sort_gen,
    quick_sort_gen,
)
from src.core.data_structures import run_ds_operations
from src.core.pseudocode import PSEUDOCODE

_benchmark_cancel_requested = threading.Event()

# ── Algorithm display-name registry ───────────────────────────────────

_ALGO_DISPLAY_NAMES = {
    "quicksort": "QuickSort",
    "heapsort": "HeapSort",
    "mergesort": "MergeSort",
    "binarysearch": "BinarySearch",
}

_DS_DISPLAY_NAMES = {
    "stack": "Stack",
    "queue": "Queue",
    "linkedlist": "LinkedList",
    "bst": "BST",
}


# ── Exposed functions ─────────────────────────────────────────────────

@eel.expose
def generate_array(size: int, input_type: str) -> List[int]:
    """Generate an array for visualisation.

    Args:
        size: Number of elements (5–200).
        input_type: ``"random"`` | ``"sorted"`` | ``"reversed"``.

    Returns:
        A list of integers of the requested distribution.
    """
    type_map = {
        "random": "Random",
        "sorted": "Sorted",
        "reversed": "Reversed",
    }
    canonical = type_map.get(input_type.lower(), "Random")
    return _generate_array(size, canonical)


@eel.expose
def get_sort_steps(
    arr: List[int],
    algorithm: str,
    options: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Run a sorting generator to completion and return all steps.

    Args:
        arr: The array to sort.
        algorithm: ``"quicksort"`` | ``"heapsort"`` | ``"mergesort"``.
        options: Optional dict with algorithm-specific options.
            For QuickSort: ``{"pivot_strategy": "first"|"last"|"middle"|"median3"}``.

    Returns:
        A list of step dicts, each JSON-serialisable via
        ``dataclasses.asdict``.
    """
    if options is None:
        options = {}

    algo_key = algorithm.lower()
    data = list(arr)

    if algo_key == "quicksort":
        pivot = options.get("pivot_strategy", "last")
        gen = quick_sort_gen(data, pivot_strategy=pivot)
    elif algo_key == "heapsort":
        gen = heap_sort_gen(data)
    elif algo_key == "mergesort":
        gen = merge_sort_gen(data)
    else:
        return []

    steps = list(gen)
    return [asdict(s) for s in steps]


@eel.expose
def get_search_steps(arr: List[int], target: int) -> List[Dict[str, Any]]:
    """Run binary_search_gen and return all steps.

    The array is sorted internally before searching.

    Args:
        arr: The array (will be sorted before search).
        target: The value to find.

    Returns:
        A list of step dicts.
    """
    sorted_arr = sorted(arr)
    steps = list(binary_search_gen(sorted_arr, int(target)))
    return [asdict(s) for s in steps]


@eel.expose
def get_pseudocode(algorithm: str) -> List[str]:
    """Return pseudo-code lines for the given algorithm.

    Args:
        algorithm: Lower-case algorithm key, e.g. ``"quicksort"``.

    Returns:
        A list of pseudo-code strings.
    """
    display = _ALGO_DISPLAY_NAMES.get(algorithm.lower(), "")
    return PSEUDOCODE.get(display, [])


@eel.expose
def run_benchmark() -> None:
    """Run the benchmark suite in a daemon thread.

    Each result line is streamed back to JS via
    ``eel.on_benchmark_line()``.
    """
    _benchmark_cancel_requested.clear()

    def _run() -> None:
        def emit(line: str) -> None:
            eel.on_benchmark_line(line)()  # call JS callback

        runner = BenchmarkRunner(
            callback=emit,
            should_cancel=_benchmark_cancel_requested.is_set,
        )
        runner.run()

    t = threading.Thread(target=_run, daemon=True)
    t.start()


@eel.expose
def cancel_benchmark() -> None:
    """Request cancellation of the running benchmark suite.

    The current timed sort run is allowed to finish; cancellation is
    checked before the next run starts.
    """
    _benchmark_cancel_requested.set()


@eel.expose
def get_sorted_array(arr: List[int]) -> List[int]:
    """Return a sorted copy of the array (used for binary search setup).

    Args:
        arr: The unsorted array.

    Returns:
        A sorted copy.
    """
    return sorted(arr)


# ── Data Structure endpoints ──────────────────────────────────────────

@eel.expose
def get_ds_steps(
    ds_type: str,
    operations: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Chạy chuỗi thao tác trên cấu trúc dữ liệu và trả về các bước.

    Args:
        ds_type: ``"stack"`` | ``"queue"`` | ``"linkedlist"`` | ``"bst"``.
        operations: Danh sách dict, mỗi dict có ``"op"`` và tùy chọn ``"value"``.

    Returns:
        Danh sách step dicts.
    """
    steps = list(run_ds_operations(ds_type.lower(), operations))
    return [asdict(s) for s in steps]


@eel.expose
def get_ds_pseudocode(ds_type: str) -> List[str]:
    """Trả về danh sách pseudo-code cho cấu trúc dữ liệu.

    Args:
        ds_type: ``"stack"`` | ``"queue"`` | ``"linkedlist"`` | ``"bst"``.

    Returns:
        Danh sách các dòng pseudo-code.
    """
    display = _DS_DISPLAY_NAMES.get(ds_type.lower(), "")
    return PSEUDOCODE.get(display, [])
