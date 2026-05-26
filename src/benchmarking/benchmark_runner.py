"""File này dùng để benchmark các thuật toán sắp xếp.

Nó tạo một mảng random lớn rồi đo thời gian chạy của từng thuật toán.
"""

from __future__ import annotations

import random
import sys
import time
from typing import Callable, Dict, List, Optional

from src.core.algorithms import (
    heap_sort_plain,
    merge_sort_plain,
    quick_sort_plain,
)


class BenchmarkRunner:
    """Lớp dùng để đo thời gian chạy của thuật toán sắp xếp.
    
    Attributes:
        n: Số phần tử trong mảng test.
        repeats: Số lần chạy mỗi thuật toán.
        callback: Hàm nhận từng dòng kết quả.
    """

    # Algorithm registry: display-name → sort function.
    ALGORITHMS: Dict[str, Callable[[List[int]], List[int]]] = {
        "QuickSort": quick_sort_plain,
        "HeapSort": heap_sort_plain,
        "MergeSort": merge_sort_plain,
    }

    def __init__(
        self,
        n: int = 1_000_000,
        repeats: int = 10,
        callback: Optional[Callable[[str], None]] = None,
        should_cancel: Optional[Callable[[], bool]] = None,
    ) -> None:
        """Tạo một đối tượng benchmark runner.
        
        Args:
            n: Số phần tử trong mảng test.
            repeats: Số lần chạy mỗi thuật toán.
            callback: Hàm nhận kết quả nếu không muốn in ra terminal.
            should_cancel: Hàm kiểm tra có cần dừng benchmark không.
        """
        self.n = n
        self.repeats = repeats
        self.callback = callback
        self.should_cancel = should_cancel or (lambda: False)

    def _emit(self, line: str) -> None:
        """Gửi một dòng kết quả ra ngoài.
        
        Args:
            line: Dòng chữ cần in hoặc gửi về giao diện.
        
        Return:
            Không trả về gì.
        """
        if self.callback is not None:
            self.callback(line)
        else:
            print(line)

    def _generate_base_array(self) -> List[int]:
        """Tạo mảng random ban đầu cho benchmark.
        
        Return:
            Một mảng số nguyên random.
        """
        return [random.randint(0, self.n) for _ in range(self.n)]

    def run(self) -> Dict[str, List[float]]:
        """Chạy benchmark cho tất cả thuật toán.
        
        Return:
            Dict chứa tên thuật toán và danh sách thời gian chạy.
        """
        base = self._generate_base_array()
        results: Dict[str, List[float]] = {}

        self._emit(
            f"Benchmarking {len(self.ALGORITHMS)} algorithms "
            f"| N = {self.n:,} | Repeats = {self.repeats}"
        )
        self._emit("=" * 50)

        for name, sort_fn in self.ALGORITHMS.items():
            if self.should_cancel():
                self._emit("\nBenchmark cancelled.")
                return results

            self._emit(f"\nRunning {name}")
            times: List[float] = []

            for i in range(1, self.repeats + 1):
                if self.should_cancel():
                    self._emit("\nBenchmark cancelled.")
                    return results

                data = list(base)  # fresh copy
                t0 = time.perf_counter()
                sort_fn(data)
                elapsed_ms = (time.perf_counter() - t0) * 1000.0
                times.append(elapsed_ms)

                # Right-align the run number for neat formatting.
                label = f"[{i}/{self.repeats}]"
                self._emit(f"  {label:>8}: {elapsed_ms:>10.2f} ms")

            avg = sum(times) / len(times)
            self._emit(f"  {'Average':>8}: {avg:>10.2f} ms")
            results[name] = times

        self._emit("\n" + "=" * 50)
        self._emit("Benchmark complete.")
        return results


# ──────────────────────────────────────────────────────────────────────
#  CLI entry-point
# ──────────────────────────────────────────────────────────────────────

def main() -> None:
    """Chạy benchmark khi gọi file bằng command line.
    
    Return:
        Không trả về gì.
    """
    runner = BenchmarkRunner()
    runner.run()


if __name__ == "__main__":
    main()
