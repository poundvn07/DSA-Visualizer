"""Các hàm tạo (generator) thuật toán để mô phỏng quá trình sắp xếp và tìm kiếm.

Mỗi hàm trong file này là một **Python generator**. Hàm nhận vào một danh sách ``list[int]`` 
(và giá trị cần tìm nếu là thuật toán tìm kiếm), sau đó sinh ra (yield) các đối tượng 
:class:`~src.core.step.Step` để mô tả từng thao tác nhỏ nhất (như so sánh, hoán đổi).

Quy tắc thiết kế
-----------------
* Danh sách ban đầu truyền vào **không bao giờ bị thay đổi**; mỗi hàm sẽ tạo một bản sao 
  để thao tác.
* ``Step.array_state`` luôn là một **bản sao mới** của danh sách tại thời điểm được sinh ra. 
  Điều này giúp an toàn khi lưu trạng thái để xem lại các bước trước đó.
* Các bộ đếm tổng số lần ``comparisons`` (so sánh) và ``swaps`` (hoán đổi) được cập nhật 
  và lưu vào từng bước (step).
"""

from __future__ import annotations

import sys
from typing import Generator, List

from src.core.step import Step

# Increase recursion limit for large-array quicksort during benchmarks.
sys.setrecursionlimit(100_000)


# ──────────────────────────────────────────────────────────────────────
#  QuickSort  (Lomuto partition scheme, configurable pivot strategy)
# ──────────────────────────────────────────────────────────────────────

def quick_sort_gen(
    arr: List[int],
    pivot_strategy: str = "last",
) -> Generator[Step, None, None]:
    """Tạo các bước mô phỏng cho thuật toán QuickSort (phân hoạch Lomuto).

    Cách phân hoạch Lomuto sẽ duyệt qua mảng con từ trái sang phải một lần duy nhất. 
    Phần tử chốt (pivot) được chọn theo ``pivot_strategy`` (chiến lược chọn chốt) 
    và sau đó được chuyển xuống cuối mảng trước khi bắt đầu phân hoạch.

    Args:
        arr: Danh sách các số nguyên cần sắp xếp. Hàm sẽ tạo một bản sao bên trong; 
            danh sách gốc không bao giờ bị thay đổi.
        pivot_strategy: Cách chọn chốt, gồm ``"first"`` (đầu), ``"last"`` (cuối), 
            ``"middle"`` (giữa), hoặc ``"median3"`` (trung vị của 3 phần tử). 
            Mặc định là ``"last"`` (Lomuto cổ điển).

    Yields:
        Step: Mỗi bước tương ứng với một lần so sánh, hoán đổi, hoặc chọn chốt.

    Example:

        for step in quick_sort_gen([5, 3, 8, 1]):
            print(step.description)
    """
    data = list(arr)
    counters = {"comparisons": 0, "swaps": 0}

    def _pick_pivot(low: int, high: int) -> int:
        """Trả về vị trí (index) của phần tử được chọn làm chốt (pivot).

        Args:
            low: Vị trí bắt đầu (bao gồm).
            high: Vị trí kết thúc (bao gồm).

        Returns:
            Vị trí của phần tử chốt được chọn.
        """
        mid = (low + high) // 2
        if pivot_strategy == "first":
            return low
        elif pivot_strategy == "middle":
            return mid
        elif pivot_strategy == "median3":
            candidates = [
                (data[low], low),
                (data[mid], mid),
                (data[high], high),
            ]
            candidates.sort(key=lambda x: x[0])
            return candidates[1][1]  # median index
        else:  # "last" (default)
            return high

    def _sub(low: int, high: int, depth: int) -> dict:
        """Tạo dict extra chứa thông tin mảng con cho renderer."""
        return {"subarray": {"left": low, "right": high, "depth": depth}}

    def _partition(
        low: int, high: int, depth: int,
    ) -> Generator[Step, None, int]:
        """Phân hoạch mảng ``data[low..high]`` theo phương pháp Lomuto.

        Phần tử chốt sẽ được đưa về vị trí cuối ``data[high]`` trước khi duyệt.

        Args:
            low: Vị trí bắt đầu (bao gồm).
            high: Vị trí kết thúc (bao gồm).
            depth: Cấp đệ quy hiện tại (0 = gốc).

        Yields:
            Step: Các bước chọn chốt, so sánh và hoán đổi.

        Returns:
            Vị trí chính xác của phần tử chốt sau khi phân hoạch xong.
        """
        # Pick pivot according to strategy and move it to the end.
        pivot_idx = _pick_pivot(low, high)
        if pivot_idx != high:
            data[pivot_idx], data[high] = data[high], data[pivot_idx]
            counters["swaps"] += 1

        pivot = data[high]
        yield Step(
            type="pivot",
            indices=[high],
            array_state=list(data),
            description=(
                f"Pivot selected: arr[{high}] = {pivot}"
                f" (strategy: {pivot_strategy})"
            ),
            highlight_line=1,
            comparisons=counters["comparisons"],
            swaps=counters["swaps"],
            extra=_sub(low, high, depth),
        )

        i = low - 1
        for j in range(low, high):
            counters["comparisons"] += 1
            cmp_sym = "≤" if data[j] <= pivot else ">"
            yield Step(
                type="compare",
                indices=[j, high],
                array_state=list(data),
                description=(
                    f"Comparing arr[{j}]={data[j]} with pivot={pivot}"
                    f" — {data[j]} {cmp_sym} {pivot}"
                ),
                highlight_line=3,
                comparisons=counters["comparisons"],
                swaps=counters["swaps"],
                extra=_sub(low, high, depth),
            )

            if data[j] <= pivot:
                i += 1
                if i != j:
                    data[i], data[j] = data[j], data[i]
                    counters["swaps"] += 1
                    yield Step(
                        type="swap",
                        indices=[i, j],
                        array_state=list(data),
                        description=(
                            f"Swapping arr[{i}]={data[i]} ↔ arr[{j}]={data[j]}"
                            f" (moving smaller element left of pivot)"
                        ),
                        highlight_line=5,
                        comparisons=counters["comparisons"],
                        swaps=counters["swaps"],
                        extra=_sub(low, high, depth),
                    )

        # Place pivot in its correct position.
        i += 1
        if i != high:
            data[i], data[high] = data[high], data[i]
            counters["swaps"] += 1
            yield Step(
                type="swap",
                indices=[i, high],
                array_state=list(data),
                description=(
                    f"Place pivot {data[i]} at position {i}"
                    f" (swap arr[{i}] ↔ arr[{high}])"
                ),
                highlight_line=7,
                comparisons=counters["comparisons"],
                swaps=counters["swaps"],
                extra=_sub(low, high, depth),
            )

        return i

    def _quicksort(
        low: int, high: int, depth: int = 0,
    ) -> Generator[Step, None, None]:
        """Hàm đệ quy thực hiện QuickSort.

        Args:
            low: Vị trí bắt đầu (bao gồm).
            high: Vị trí kết thúc (bao gồm).
            depth: Cấp đệ quy hiện tại.

        Yields:
            Step: Tất cả các bước phân hoạch và gọi đệ quy.
        """
        if low < high:
            # _partition is a generator that returns its final value via
            # ``return``.  We capture that value with a wrapper pattern.
            part_gen = _partition(low, high, depth)
            pivot_index = None
            try:
                while True:
                    step = next(part_gen)
                    yield step
            except StopIteration as exc:
                pivot_index = exc.value

            yield from _quicksort(low, pivot_index - 1, depth + 1)
            yield from _quicksort(pivot_index + 1, high, depth + 1)

    if len(data) > 1:
        yield from _quicksort(0, len(data) - 1)


# ──────────────────────────────────────────────────────────────────────
#  HeapSort
# ──────────────────────────────────────────────────────────────────────

def heap_sort_gen(arr: List[int]) -> Generator[Step, None, None]:
    """Tạo các bước mô phỏng cho thuật toán HeapSort (Sắp xếp vun đống).

    Thuật toán HeapSort diễn ra trong 2 giai đoạn:

    1. **Tạo max-heap (đống lớn nhất)** — gọi hàm ``sift_down`` từ nút cha cuối cùng 
       ngược lên nút gốc để tạo cấu trúc đống.
    2. **Trích xuất phần tử lớn nhất** — liên tục hoán đổi nút gốc (phần tử lớn nhất) 
       xuống cuối mảng (phần chưa sắp xếp) và vun đống lại từ đầu.

    Args:
        arr: Danh sách các số nguyên cần sắp xếp. Hàm sẽ tạo một bản sao bên trong.

    Yields:
        Step: Mỗi bước tương ứng với một lần so sánh hoặc hoán đổi khi vun đống và trích xuất.

    Example:

        for step in heap_sort_gen([4, 10, 3, 5, 1]):
            print(step.description)
    """
    data = list(arr)
    n = len(data)
    counters = {"comparisons": 0, "swaps": 0}

    def _sift_down(start: int, end: int) -> Generator[Step, None, None]:
        """Vun đống phần tử tại vị trí *start* xuống dưới để duy trì tính chất của đống.

        Args:
            start: Vị trí của phần tử cần vun xuống.
            end: Vị trí hợp lệ cuối cùng trong vùng đang xét của đống.

        Yields:
            Step: Các bước so sánh và hoán đổi.
        """
        root = start
        while True:
            child = 2 * root + 1
            if child > end:
                break

            # Pick the larger child.
            if child + 1 <= end:
                counters["comparisons"] += 1
                left_val = data[child]
                right_val = data[child + 1]
                larger = "right" if right_val > left_val else "left"
                yield Step(
                    type="compare",
                    indices=[child, child + 1],
                    array_state=list(data),
                    description=(
                        f"Heapify: comparing children"
                        f" arr[{child}]={left_val} and"
                        f" arr[{child + 1}]={right_val}"
                        f" — {larger} child is larger"
                    ),
                    highlight_line=3,
                    comparisons=counters["comparisons"],
                    swaps=counters["swaps"],
                )
                if data[child + 1] > data[child]:
                    child += 1

            # Compare root with the larger child.
            counters["comparisons"] += 1
            root_val = data[root]
            child_val = data[child]
            needs_swap = root_val < child_val
            yield Step(
                type="compare",
                indices=[root, child],
                array_state=list(data),
                description=(
                    f"Heapify: {child_val} is {'larger' if needs_swap else 'not larger'}"
                    f" than parent {root_val}"
                    f"{', sifting down' if needs_swap else ', heap property holds'}"
                ),
                highlight_line=5,
                comparisons=counters["comparisons"],
                swaps=counters["swaps"],
            )

            if needs_swap:
                data[root], data[child] = data[child], data[root]
                counters["swaps"] += 1
                yield Step(
                    type="swap",
                    indices=[root, child],
                    array_state=list(data),
                    description=(
                        f"Heapify: swap arr[{root}]={data[root]}"
                        f" ↔ arr[{child}]={data[child]}"
                    ),
                    highlight_line=6,
                    comparisons=counters["comparisons"],
                    swaps=counters["swaps"],
                )
                root = child
            else:
                break

    # Phase 1: Build max-heap.
    for start_idx in range(n // 2 - 1, -1, -1):
        yield from _sift_down(start_idx, n - 1)

    # Phase 2: Extract max elements.
    for end_idx in range(n - 1, 0, -1):
        data[0], data[end_idx] = data[end_idx], data[0]
        counters["swaps"] += 1
        yield Step(
            type="swap",
            indices=[0, end_idx],
            array_state=list(data),
            description=(
                f"Extract max: move {data[end_idx]} to position {end_idx}"
                f" (swap arr[0] ↔ arr[{end_idx}])"
            ),
            highlight_line=9,
            comparisons=counters["comparisons"],
            swaps=counters["swaps"],
        )
        yield from _sift_down(0, end_idx - 1)


# ──────────────────────────────────────────────────────────────────────
#  MergeSort  (top-down, iterative merge)
# ──────────────────────────────────────────────────────────────────────

def merge_sort_gen(arr: List[int]) -> Generator[Step, None, None]:
    """Tạo các bước mô phỏng cho thuật toán MergeSort (từ trên xuống).

    Vì MergeSort **không** phải là thuật toán sắp xếp tại chỗ (in-place), chúng ta 
    duy trì một danh sách ``data`` chung và thực hiện gộp bằng cách ghi đè trực tiếp 
    lên nó. Mỗi lần đặt một phần tử vào mảng trong lúc gộp sẽ tạo ra một bước ``"set"``.

    Args:
        arr: Danh sách các số nguyên cần sắp xếp. Hàm sẽ tạo một bản sao bên trong.

    Yields:
        Step: Mỗi bước tương ứng với một lần so sánh hoặc đặt phần tử trong quá trình gộp.

    Example:

        for step in merge_sort_gen([38, 27, 43, 3, 9, 82, 10]):
            print(step.description)
    """
    data = list(arr)
    counters = {"comparisons": 0, "swaps": 0}

    def _sub(left: int, right: int, depth: int) -> dict:
        """Tạo dict extra chứa thông tin mảng con cho renderer."""
        return {"subarray": {"left": left, "right": right, "depth": depth}}

    def _merge_sort(
        left: int, right: int, depth: int = 0,
    ) -> Generator[Step, None, None]:
        """Đệ quy chia đôi và gộp mảng ``data[left..right]``.

        Args:
            left: Vị trí bắt đầu (bao gồm).
            right: Vị trí kết thúc (bao gồm).
            depth: Cấp đệ quy hiện tại.

        Yields:
            Step: Các bước so sánh và đặt phần tử trong mỗi lần gộp.
        """
        if left >= right:
            return

        mid = (left + right) // 2
        yield from _merge_sort(left, mid, depth + 1)
        yield from _merge_sort(mid + 1, right, depth + 1)
        yield from _merge(left, mid, right, depth)

    def _merge(
        left: int, mid: int, right: int, depth: int,
    ) -> Generator[Step, None, None]:
        """Gộp hai nửa đã được sắp xếp là ``data[left..mid]`` và ``data[mid+1..right]``.

        Args:
            left: Vị trí bắt đầu của nửa trái.
            mid: Vị trí kết thúc của nửa trái.
            right: Vị trí kết thúc của nửa phải.
            depth: Cấp đệ quy hiện tại.

        Yields:
            Step: Một bước ``"compare"`` (so sánh) cho mỗi cặp và một bước ``"set"`` (đặt) 
            cho mỗi phần tử được ghi lại vào ``data``.
        """
        merged: List[int] = []
        i, j = left, mid + 1

        while i <= mid and j <= right:
            counters["comparisons"] += 1
            left_val = data[i]
            right_val = data[j]
            takes_left = left_val <= right_val
            yield Step(
                type="compare",
                indices=[i, j],
                array_state=list(data),
                description=(
                    f"Merge: comparing arr[{i}]={left_val} and"
                    f" arr[{j}]={right_val}"
                    f" — taking {'left' if takes_left else 'right'}"
                ),
                highlight_line=4,
                comparisons=counters["comparisons"],
                swaps=counters["swaps"],
                extra=_sub(left, right, depth),
            )
            if takes_left:
                merged.append(data[i])
                i += 1
            else:
                merged.append(data[j])
                j += 1

        while i <= mid:
            merged.append(data[i])
            i += 1
        while j <= right:
            merged.append(data[j])
            j += 1

        # Write merged elements back into the data array.
        for k, val in enumerate(merged):
            data[left + k] = val
            counters["swaps"] += 1  # counted as a "write" / placement
            yield Step(
                type="set",
                indices=[left + k],
                array_state=list(data),
                description=(
                    f"Placing {val} into position arr[{left + k}]"
                    f" (merged write-back)"
                ),
                highlight_line=8,
                comparisons=counters["comparisons"],
                swaps=counters["swaps"],
                extra=_sub(left, right, depth),
            )

    if len(data) > 1:
        yield from _merge_sort(0, len(data) - 1)


# ──────────────────────────────────────────────────────────────────────
#  Binary Search
# ──────────────────────────────────────────────────────────────────────

def binary_search_gen(
    arr: List[int], target: int
) -> Generator[Step, None, None]:
    """Tạo các bước mô phỏng cho thuật toán Tìm kiếm nhị phân (Binary Search).

    Mảng đầu vào **bắt buộc** phải được sắp xếp tăng dần. Mỗi bước sẽ trả về 
    khoảng đang xét ``[low, mid, high]`` để giao diện (UI) có thể làm nổi bật 
    vùng tìm kiếm hiện tại.

    Args:
        arr: Danh sách các số nguyên **đã được sắp xếp** cần tìm kiếm.
        target: Giá trị số nguyên cần tìm.

    Yields:
        Step: Mỗi bước là một vòng lặp cho thấy khoảng đang xét và kết quả so sánh. 
        Bước cuối cùng sẽ có loại là ``"found"`` (đã tìm thấy) hoặc ``"not_found"`` (không tìm thấy).

    Example:

        for step in binary_search_gen([1, 3, 5, 7, 9], 5):
            print(step.description)
    """
    data = list(arr)
    low, high = 0, len(data) - 1
    comparisons = 0

    while low <= high:
        mid = (low + high) // 2

        # Show current search range.
        yield Step(
            type="range",
            indices=[low, mid, high],
            array_state=list(data),
            description=(
                f"Search range: low={low}, mid={mid}, high={high}"
                f" (window size {high - low + 1})"
            ),
            highlight_line=2,
            comparisons=comparisons,
            swaps=0,
        )

        comparisons += 1

        if data[mid] == target:
            yield Step(
                type="found",
                indices=[mid],
                array_state=list(data),
                description=(
                    f"arr[{mid}] = {data[mid]} matches target {target}"
                    f" — found at index {mid}"
                ),
                highlight_line=4,
                comparisons=comparisons,
                swaps=0,
            )
            return
        elif data[mid] < target:
            yield Step(
                type="compare",
                indices=[mid],
                array_state=list(data),
                description=(
                    f"arr[{mid}] = {data[mid]} < target {target}"
                    f", eliminating left half"
                ),
                highlight_line=6,
                comparisons=comparisons,
                swaps=0,
            )
            low = mid + 1
        else:
            yield Step(
                type="compare",
                indices=[mid],
                array_state=list(data),
                description=(
                    f"arr[{mid}] = {data[mid]} > target {target}"
                    f", eliminating right half"
                ),
                highlight_line=8,
                comparisons=comparisons,
                swaps=0,
            )
            high = mid - 1

    yield Step(
        type="not_found",
        indices=[],
        array_state=list(data),
        description=(
            f"Search space exhausted — target {target} is not in the array"
        ),
        highlight_line=10,
        comparisons=comparisons,
        swaps=0,
    )


# ──────────────────────────────────────────────────────────────────────
#  Plain (non-generator) sort functions for benchmarking
# ──────────────────────────────────────────────────────────────────────

def quick_sort_plain(arr: List[int]) -> List[int]:
    """Thuật toán QuickSort chạy trực tiếp (in-place) không kèm mô phỏng.

    Sử dụng phương pháp phân hoạch Lomuto, giống hệt với hàm :func:`quick_sort_gen`
    nhưng không sinh ra các bước để phục vụ cho việc tính toán hiệu năng (benchmark).

    Args:
        arr: Danh sách cần sắp xếp **trực tiếp** (in-place).

    Returns:
        Cùng là danh sách đó, nhưng đã được sắp xếp tăng dần.
    """
    def _partition(low: int, high: int) -> int:
        pivot = arr[high]
        i = low - 1
        for j in range(low, high):
            if arr[j] <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1

    def _qs(low: int, high: int) -> None:
        if low < high:
            p = _partition(low, high)
            _qs(low, p - 1)
            _qs(p + 1, high)

    _qs(0, len(arr) - 1)
    return arr


def heap_sort_plain(arr: List[int]) -> List[int]:
    """Thuật toán HeapSort chạy trực tiếp (in-place) không kèm mô phỏng.

    Args:
        arr: Danh sách cần sắp xếp **trực tiếp** (in-place).

    Returns:
        Cùng là danh sách đó, nhưng đã được sắp xếp tăng dần.
    """
    n = len(arr)

    def _sift_down(start: int, end: int) -> None:
        root = start
        while True:
            child = 2 * root + 1
            if child > end:
                break
            if child + 1 <= end and arr[child + 1] > arr[child]:
                child += 1
            if arr[root] < arr[child]:
                arr[root], arr[child] = arr[child], arr[root]
                root = child
            else:
                break

    for i in range(n // 2 - 1, -1, -1):
        _sift_down(i, n - 1)
    for end in range(n - 1, 0, -1):
        arr[0], arr[end] = arr[end], arr[0]
        _sift_down(0, end - 1)
    return arr


def merge_sort_plain(arr: List[int]) -> List[int]:
    """Thuật toán MergeSort (từ trên xuống) không kèm mô phỏng.

    Args:
        arr: Danh sách cần sắp xếp **trực tiếp** (thông qua gộp theo vị trí chỉ mục).

    Returns:
        Cùng là danh sách đó, nhưng đã được sắp xếp tăng dần.
    """
    def _merge_sort(left: int, right: int) -> None:
        if left >= right:
            return
        mid = (left + right) // 2
        _merge_sort(left, mid)
        _merge_sort(mid + 1, right)
        merged = []
        i, j = left, mid + 1
        while i <= mid and j <= right:
            if arr[i] <= arr[j]:
                merged.append(arr[i])
                i += 1
            else:
                merged.append(arr[j])
                j += 1
        while i <= mid:
            merged.append(arr[i])
            i += 1
        while j <= right:
            merged.append(arr[j])
            j += 1
        for k, val in enumerate(merged):
            arr[left + k] = val

    _merge_sort(0, len(arr) - 1)
    return arr
