"""File này là cầu nối giữa JavaScript và Python.

Các hàm có ``@eel.expose`` sẽ được giao diện web gọi. Em dùng file này để lấy mảng, lấy các bước mô phỏng, chạy benchmark và chạy cấu trúc dữ liệu.
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
    """Tạo mảng theo kiểu được chọn.
    
    Args:
        n: Số phần tử cần tạo.
        input_type: Kiểu mảng, gồm ``Random``, ``Sorted`` hoặc ``Reversed``.
        low: Giá trị nhỏ nhất có thể có.
        high: Giá trị lớn nhất có thể có.
    
    Return:
        Một mảng số nguyên theo đúng kiểu được chọn.
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
    """Chạy thuật toán sắp xếp và lấy các bước mô phỏng.
    
    Args:
        arr: Mảng cần sắp xếp.
        algorithm: Tên thuật toán cần chạy.
        options: Tùy chọn thêm, ví dụ cách chọn pivot của QuickSort.
    
    Return:
        Danh sách các bước ở dạng dict.
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
    """Chạy tìm kiếm nhị phân và lấy các bước mô phỏng.
    
    Args:
        arr: Mảng ban đầu, hàm sẽ sắp xếp trước khi tìm.
        target: Giá trị cần tìm.
    
    Return:
        Danh sách các bước ở dạng dict.
    """
    sorted_arr = sorted(arr)
    steps = list(binary_search_gen(sorted_arr, int(target)))
    return [asdict(s) for s in steps]


@eel.expose
def get_pseudocode(algorithm: str) -> List[str]:
    """Lấy giả mã của thuật toán.
    
    Args:
        algorithm: Tên thuật toán ở dạng chữ thường.
    
    Return:
        Danh sách các dòng giả mã.
    """
    display = _ALGO_DISPLAY_NAMES.get(algorithm.lower(), "")
    return PSEUDOCODE.get(display, [])


@eel.expose
def run_benchmark() -> None:
    """Chạy benchmark trong một luồng riêng.
    
    Return:
        Không trả về gì.
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
    """Yêu cầu dừng benchmark.
    
    Return:
        Không trả về gì.
    """
    _benchmark_cancel_requested.set()


@eel.expose
def get_sorted_array(arr: List[int]) -> List[int]:
    """Tạo bản sao đã sắp xếp của mảng.
    
    Args:
        arr: Mảng ban đầu.
    
    Return:
        Mảng mới đã được sắp xếp tăng dần.
    """
    return sorted(arr)


# ── Data Structure endpoints ──────────────────────────────────────────

@eel.expose
def get_ds_steps(
    ds_type: str,
    operations: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Chạy các thao tác trên cấu trúc dữ liệu.
    
    Args:
        ds_type: Loại cấu trúc dữ liệu.
        operations: Danh sách thao tác cần chạy.
    
    Return:
        Danh sách các bước ở dạng dict.
    """
    steps = list(run_ds_operations(ds_type.lower(), operations))
    return [asdict(s) for s in steps]


@eel.expose
def get_ds_pseudocode(ds_type: str) -> List[str]:
    """Lấy giả mã của cấu trúc dữ liệu.
    
    Args:
        ds_type: Loại cấu trúc dữ liệu.
    
    Return:
        Danh sách các dòng giả mã.
    """
    display = _DS_DISPLAY_NAMES.get(ds_type.lower(), "")
    return PSEUDOCODE.get(display, [])
