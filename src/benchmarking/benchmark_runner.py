"""Benchmark runner for sorting algorithms.

Generates a random list of 1 000 000 integers and times QuickSort,
HeapSort, and MergeSort over 10 independent runs each.  Results are
printed in a standardised format and optionally streamed to a callback
for GUI consumption.

Usage::

    # From the command line:
    python -m src.benchmarking.benchmark_runner

    # Programmatically (e.g. from the GUI):
    from src.benchmarking.benchmark_runner import BenchmarkRunner
    runner = BenchmarkRunner(callback=print)
    runner.run()
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
    """Runs timed benchmarks on sorting algorithms.

    Attributes:
        n: Number of elements in the test array (default 1 000 000).
        repeats: How many times each algorithm is run (default 10).
        callback: An optional function called with each output line.
            When ``None``, output goes to ``sys.stdout``.

    Example::

        runner = BenchmarkRunner(n=500_000, repeats=5)
        runner.run()
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
        """Initialise the benchmark runner.

        Args:
            n: Size of the array to sort.
            repeats: Number of independent timed runs per algorithm.
            callback: If provided, each output line is passed to this
                callable instead of being printed to stdout.
            should_cancel: Optional predicate checked between timed runs.
        """
        self.n = n
        self.repeats = repeats
        self.callback = callback
        self.should_cancel = should_cancel or (lambda: False)

    def _emit(self, line: str) -> None:
        """Send one line of output to the callback or stdout.

        Args:
            line: The formatted string to emit (no trailing newline).
        """
        if self.callback is not None:
            self.callback(line)
        else:
            print(line)

    def _generate_base_array(self) -> List[int]:
        """Create the master random array of ``self.n`` integers.

        Returns:
            A ``list[int]`` of length ``self.n`` with values in
            ``[0, self.n)``.
        """
        return [random.randint(0, self.n) for _ in range(self.n)]

    def run(self) -> Dict[str, List[float]]:
        """Execute the full benchmark suite.

        For each registered algorithm the method:

        1. Prints a header line.
        2. Runs the sort ``self.repeats`` times on a **fresh copy** of
           the master array.
        3. Prints the elapsed time for each run.

        Returns:
            A dictionary mapping algorithm names to lists of elapsed
            times (in milliseconds).
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
    """Run benchmarks from the command line.

    Invoked via ``python -m src.benchmarking.benchmark_runner``.
    """
    runner = BenchmarkRunner()
    runner.run()


if __name__ == "__main__":
    main()
