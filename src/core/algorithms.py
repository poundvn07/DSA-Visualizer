"""Các thuật toán dùng cho phần mô phỏng và benchmark.

File này có hai loại hàm:
- Hàm có đuôi ``_gen``: tạo ra từng bước để giao diện vẽ.
- Hàm có đuôi ``_plain``: chỉ sắp xếp mảng, không tạo bước.
"""

import sys
from typing import Generator, List

from src.core.step import Step

sys.setrecursionlimit(100_000)


def quick_sort_gen(
    arr: List[int],
    pivot_strategy: str = "last",
) -> Generator[Step, None, None]:
    """Tạo các bước mô phỏng cho thuật toán QuickSort.
    
    Hàm này copy mảng ban đầu rồi sắp xếp bằng QuickSort. Trong lúc chạy, hàm tạo Step để giao diện thấy bước chọn pivot, so sánh và đổi chỗ.
    
    Args:
        arr: Mảng số nguyên cần sắp xếp.
        pivot_strategy: Cách chọn pivot, gồm ``first``, ``last``, ``middle`` hoặc ``median3``.
    
    Yield:
        Step: Một bước mô phỏng của QuickSort.
    """
    data = list(arr)
    comparisons = 0
    swaps = 0

    def choose_pivot(first: int, last: int) -> int:
        """Chọn vị trí pivot cho đoạn mảng hiện tại.
        
        Args:
            first: Vị trí đầu của đoạn mảng.
            last: Vị trí cuối của đoạn mảng.
        
        Return:
            Vị trí của phần tử được chọn làm pivot.
        """
        mid = (first + last) // 2
        if pivot_strategy == "first":
            return first
        elif pivot_strategy == "middle":
            return mid
        elif pivot_strategy == "median3":
            choices = [(data[first], first), (data[mid], mid), (data[last], last)]
            choices.sort()
            return choices[1][1]
        return last

    def subarray(first: int, last: int, depth: int) -> dict:
        """Tạo thông tin đoạn mảng đang xử lý.
        
        Args:
            first: Vị trí đầu của đoạn mảng.
            last: Vị trí cuối của đoạn mảng.
            depth: Độ sâu đệ quy hiện tại.
        
        Return:
            Dict chứa thông tin đoạn mảng.
        """
        return {"subarray": {"left": first, "right": last, "depth": depth}}

    def partition(first: int, last: int, depth: int) -> Generator[Step, None, int]:
        """Chia đoạn mảng thành hai bên theo pivot.
        
        Args:
            first: Vị trí đầu của đoạn mảng.
            last: Vị trí cuối của đoạn mảng.
            depth: Độ sâu đệ quy hiện tại.
        
        Yield:
            Step: Các bước chọn pivot, so sánh và đổi chỗ.
        
        Return:
            Vị trí cuối cùng của pivot.
        """
        nonlocal comparisons, swaps

        pivot_index = choose_pivot(first, last)
        if pivot_index != first:
            data[first], data[pivot_index] = data[pivot_index], data[first]
            swaps += 1

        pivot_value = data[first]
        yield Step(
            type="pivot",
            indices=[first],
            array_state=list(data),
            description=(
                f"Pivot selected: arr[{first}] = {pivot_value}"
                f" (strategy: {pivot_strategy})"
            ),
            highlight_line=1,
            comparisons=comparisons,
            swaps=swaps,
            extra=subarray(first, last, depth),
        )

        left_mark = first + 1
        right_mark = last
        done = False

        while not done:
            while left_mark <= right_mark:
                comparisons += 1
                yield Step(
                    type="compare",
                    indices=[left_mark, first],
                    array_state=list(data),
                    description=(
                        f"Comparing arr[{left_mark}]={data[left_mark]} with pivot={pivot_value}"
                        f" — {data[left_mark]} {'≤' if data[left_mark] <= pivot_value else '>'} {pivot_value}"
                    ),
                    highlight_line=3,
                    comparisons=comparisons,
                    swaps=swaps,
                    extra=subarray(first, last, depth),
                )
                if data[left_mark] <= pivot_value:
                    left_mark += 1
                else:
                    break

            while right_mark >= left_mark:
                comparisons += 1
                yield Step(
                    type="compare",
                    indices=[right_mark, first],
                    array_state=list(data),
                    description=(
                        f"Comparing arr[{right_mark}]={data[right_mark]} with pivot={pivot_value}"
                        f" — {data[right_mark]} {'≥' if data[right_mark] >= pivot_value else '<'} {pivot_value}"
                    ),
                    highlight_line=3,
                    comparisons=comparisons,
                    swaps=swaps,
                    extra=subarray(first, last, depth),
                )
                if data[right_mark] >= pivot_value:
                    right_mark -= 1
                else:
                    break

            if right_mark < left_mark:
                done = True
            else:
                data[left_mark], data[right_mark] = data[right_mark], data[left_mark]
                swaps += 1
                yield Step(
                    type="swap",
                    indices=[left_mark, right_mark],
                    array_state=list(data),
                    description=(
                        f"Swapping arr[{left_mark}]={data[left_mark]}"
                        f" ↔ arr[{right_mark}]={data[right_mark]}"
                    ),
                    highlight_line=5,
                    comparisons=comparisons,
                    swaps=swaps,
                    extra=subarray(first, last, depth),
                )

        if first != right_mark:
            data[first], data[right_mark] = data[right_mark], data[first]
            swaps += 1
            yield Step(
                type="swap",
                indices=[first, right_mark],
                array_state=list(data),
                description=(
                    f"Place pivot {data[right_mark]} at position {right_mark}"
                    f" (swap arr[{first}] ↔ arr[{right_mark}])"
                ),
                highlight_line=7,
                comparisons=comparisons,
                swaps=swaps,
                extra=subarray(first, last, depth),
            )
        return right_mark

    def quick_sort_helper(first: int, last: int, depth: int = 0) -> Generator[Step, None, None]:
        """Gọi QuickSort cho một đoạn nhỏ trong mảng.
        
        Args:
            first: Vị trí đầu của đoạn mảng.
            last: Vị trí cuối của đoạn mảng.
            depth: Độ sâu đệ quy hiện tại.
        
        Yield:
            Step: Các bước mô phỏng trong đoạn mảng này.
        """
        if first < last:
            pivot_index = yield from partition(first, last, depth)
            yield from quick_sort_helper(first, pivot_index - 1, depth + 1)
            yield from quick_sort_helper(pivot_index + 1, last, depth + 1)

    yield from quick_sort_helper(0, len(data) - 1)


def heap_sort_gen(arr: List[int]) -> Generator[Step, None, None]:
    """Tạo các bước mô phỏng cho thuật toán HeapSort.
    
    Hàm này copy mảng ban đầu, tạo max heap rồi đưa phần tử lớn nhất về cuối mảng từng lần.
    
    Args:
        arr: Mảng số nguyên cần sắp xếp.
    
    Yield:
        Step: Một bước so sánh hoặc đổi chỗ của HeapSort.
    """
    data = list(arr)
    comparisons = 0
    swaps = 0
    n = len(data)

    def heapify(heap_size: int, i: int) -> Generator[Step, None, None]:
        """Sửa lại heap bắt đầu từ một vị trí.
        
        Args:
            heap_size: Số phần tử còn nằm trong heap.
            i: Vị trí gốc đang cần kiểm tra.
        
        Yield:
            Step: Các bước so sánh và đổi chỗ khi sửa heap.
        """
        nonlocal comparisons, swaps

        largest = i
        left = 2 * i + 1
        right = 2 * i + 2

        if left < heap_size:
            comparisons += 1
            left_is_larger = data[left] > data[largest]
            yield Step(
                type="compare",
                indices=[left, largest],
                array_state=list(data),
                description=(
                    f"Heapify: arr[{left}]={data[left]} is "
                    f"{'larger' if left_is_larger else 'not larger'} than arr[{largest}]={data[largest]}"
                ),
                highlight_line=5,
                comparisons=comparisons,
                swaps=swaps,
            )
            if left_is_larger:
                largest = left

        if right < heap_size:
            comparisons += 1
            right_is_larger = data[right] > data[largest]
            yield Step(
                type="compare",
                indices=[right, largest],
                array_state=list(data),
                description=(
                    f"Heapify: arr[{right}]={data[right]} is "
                    f"{'larger' if right_is_larger else 'not larger'} than arr[{largest}]={data[largest]}"
                ),
                highlight_line=5,
                comparisons=comparisons,
                swaps=swaps,
            )
            if right_is_larger:
                largest = right

        if largest != i:
            data[i], data[largest] = data[largest], data[i]
            swaps += 1
            yield Step(
                type="swap",
                indices=[i, largest],
                array_state=list(data),
                description=(
                    f"Heapify: swap arr[{i}]={data[i]}"
                    f" ↔ arr[{largest}]={data[largest]}"
                ),
                highlight_line=6,
                comparisons=comparisons,
                swaps=swaps,
            )
            yield from heapify(heap_size, largest)

    for i in range(n // 2 - 1, -1, -1):
        yield from heapify(n, i)

    for i in range(n - 1, 0, -1):
        data[0], data[i] = data[i], data[0]
        swaps += 1
        yield Step(
            type="swap",
            indices=[0, i],
            array_state=list(data),
            description=(
                f"Extract max: move {data[i]} to position {i}"
                f" (swap arr[0] ↔ arr[{i}])"
            ),
            highlight_line=9,
            comparisons=comparisons,
            swaps=swaps,
        )
        yield from heapify(i, 0)


def merge_sort_gen(arr: List[int]) -> Generator[Step, None, None]:
    """Tạo các bước mô phỏng cho thuật toán MergeSort.
    
    Hàm này copy mảng ban đầu, chia mảng thành hai nửa rồi gộp lại theo thứ tự tăng dần.
    
    Args:
        arr: Mảng số nguyên cần sắp xếp.
    
    Yield:
        Step: Một bước so sánh hoặc ghi giá trị của MergeSort.
    """
    data = list(arr)
    comparisons = 0
    swaps = 0

    def subarray(left: int, right: int, depth: int) -> dict:
        """Tạo thông tin đoạn mảng đang xử lý.
        
        Args:
            left: Vị trí đầu của đoạn mảng.
            right: Vị trí cuối của đoạn mảng.
            depth: Độ sâu đệ quy hiện tại.
        
        Return:
            Dict chứa thông tin đoạn mảng.
        """
        return {"subarray": {"left": left, "right": right, "depth": depth}}

    def merge_sort_helper(left: int, right: int, depth: int = 0) -> Generator[Step, None, None]:
        """Chia mảng thành hai nửa rồi gộp lại.
        
        Args:
            left: Vị trí bắt đầu của đoạn mảng.
            right: Vị trí kết thúc, không lấy vị trí này.
            depth: Độ sâu đệ quy hiện tại.
        
        Yield:
            Step: Các bước so sánh và ghi lại khi gộp mảng.
        """
        nonlocal comparisons, swaps

        if right - left <= 1:
            return

        mid = (left + right) // 2
        yield from merge_sort_helper(left, mid, depth + 1)
        yield from merge_sort_helper(mid, right, depth + 1)

        left_half = data[left:mid]
        right_half = data[mid:right]
        i = 0
        j = 0
        k = left

        while i < len(left_half) and j < len(right_half):
            comparisons += 1
            left_index = left + i
            right_index = mid + j
            take_left = left_half[i] <= right_half[j]
            yield Step(
                type="compare",
                indices=[left_index, right_index],
                array_state=list(data),
                description=(
                    f"Merge: comparing arr[{left_index}]={left_half[i]} and"
                    f" arr[{right_index}]={right_half[j]}"
                    f" — taking {'left' if take_left else 'right'}"
                ),
                highlight_line=4,
                comparisons=comparisons,
                swaps=swaps,
                extra=subarray(left, right - 1, depth),
            )
            if take_left:
                data[k] = left_half[i]
                i += 1
            else:
                data[k] = right_half[j]
                j += 1
            swaps += 1
            yield Step(
                type="set",
                indices=[k],
                array_state=list(data),
                description=f"Placing {data[k]} into position arr[{k}] (merged write-back)",
                highlight_line=8,
                comparisons=comparisons,
                swaps=swaps,
                extra=subarray(left, right - 1, depth),
            )
            k += 1

        while i < len(left_half):
            data[k] = left_half[i]
            i += 1
            swaps += 1
            yield Step(
                type="set",
                indices=[k],
                array_state=list(data),
                description=f"Placing {data[k]} into position arr[{k}] (merged write-back)",
                highlight_line=8,
                comparisons=comparisons,
                swaps=swaps,
                extra=subarray(left, right - 1, depth),
            )
            k += 1

        while j < len(right_half):
            data[k] = right_half[j]
            j += 1
            swaps += 1
            yield Step(
                type="set",
                indices=[k],
                array_state=list(data),
                description=f"Placing {data[k]} into position arr[{k}] (merged write-back)",
                highlight_line=8,
                comparisons=comparisons,
                swaps=swaps,
                extra=subarray(left, right - 1, depth),
            )
            k += 1

    yield from merge_sort_helper(0, len(data))


def binary_search_gen(
    arr: List[int], target: int
) -> Generator[Step, None, None]:
    """Tạo các bước mô phỏng cho thuật toán tìm kiếm nhị phân.
    
    Hàm này tìm target trong mảng đã được sắp xếp tăng dần.
    
    Args:
        arr: Mảng số nguyên đã được sắp xếp.
        target: Giá trị cần tìm.
    
    Yield:
        Step: Một bước mô phỏng quá trình tìm kiếm.
    """
    data = list(arr)
    low = 0
    high = len(data) - 1
    comparisons = 0

    while low <= high:
        mid = (low + high) // 2
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

        if data[mid] < target:
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


def quick_sort_plain(arr):
    """Sắp xếp mảng bằng QuickSort.
    
    Args:
        arr: Mảng cần sắp xếp trực tiếp.
    
    Return:
        Chính mảng arr sau khi đã sắp xếp.
    """
    quick_sort_helper(arr, 0, len(arr) - 1)
    return arr

def quick_sort_helper(arr, first, last):
    """Gọi QuickSort cho một đoạn nhỏ trong mảng.
    
    Args:
        arr: Mảng đang được sắp xếp.
        first: Vị trí đầu của đoạn mảng.
        last: Vị trí cuối của đoạn mảng.
    """
    if first < last:
        pivot_index = partition(arr, first, last)
        quick_sort_helper(arr, first, pivot_index - 1)
        quick_sort_helper(arr, pivot_index + 1, last)

def partition(arr, first, last):
    """Chia mảng thành hai phía dựa vào pivot.
    
    Args:
        arr: Mảng đang được sắp xếp.
        first: Vị trí đầu của đoạn mảng.
        last: Vị trí cuối của đoạn mảng.
    
    Return:
        Vị trí cuối cùng của pivot.
    """
    pivot_value = median_of_three(arr, first, last)
    left_mark = first + 1
    right_mark = last
    done = False
    while not done:
        while left_mark <= right_mark and arr[left_mark] <= pivot_value:
            left_mark += 1
        while arr[right_mark] >= pivot_value and right_mark >= left_mark:
            right_mark -= 1
        if right_mark < left_mark:
            done = True
        else:
            arr[left_mark], arr[right_mark] = arr[right_mark], arr[left_mark]
    arr[first], arr[right_mark] = arr[right_mark], arr[first]
    return right_mark

def median_of_three(arr, first, last):
    """Chọn pivot bằng cách lấy trung vị của ba phần tử.
    
    Args:
        arr: Mảng đang được sắp xếp.
        first: Vị trí đầu của đoạn mảng.
        last: Vị trí cuối của đoạn mảng.
    
    Return:
        Giá trị pivot được chọn.
    """
    mid = (first + last) // 2

    if arr[first] > arr[mid]:
        arr[first], arr[mid] = arr[mid], arr[first]
    if arr[first] > arr[last]:
        arr[first], arr[last] = arr[last], arr[first]
    if arr[mid] > arr[last]:
        arr[mid], arr[last] = arr[last], arr[mid]

    arr[first], arr[mid] = arr[mid], arr[first]

    return arr[first]

def heap_sort_plain(arr):
    """Sắp xếp mảng bằng HeapSort.
    
    Args:
        arr: Mảng cần sắp xếp trực tiếp.
    
    Return:
        Chính mảng arr sau khi đã sắp xếp.
    """
    n = len(arr)

    def heapify(a, n, i):
        """Sửa lại heap từ một vị trí.
        
        Args:
            a: Mảng đang được xử lý.
            n: Số phần tử trong heap.
            i: Vị trí gốc đang cần kiểm tra.
        """
        largest = i
        l, r = 2*i+1, 2*i+2
        if l < n and a[l] > a[largest]:
            largest = l
        if r < n and a[r] > a[largest]:
            largest = r
        if largest != i:
            a[i], a[largest] = a[largest], a[i]
            heapify(a, n, largest)

    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        heapify(arr, n, 0)
    return arr

def merge_sort_plain(arr):
    """Sắp xếp mảng bằng MergeSort.
    
    Args:
        arr: Mảng cần sắp xếp trực tiếp.
    
    Return:
        Chính mảng arr sau khi đã sắp xếp.
    """
    if len(arr) > 1:
        mid = len(arr) // 2
        left_half = arr[:mid]
        right_half = arr[mid:]

        merge_sort_plain(left_half)
        merge_sort_plain(right_half)
        i = 0
        j = 0
        k = 0
        while i < len(left_half) and j < len(right_half):
            if left_half[i] < right_half[j]:
                arr[k] = left_half[i]
                i += 1
            else:
                arr[k] = right_half[j]
                j += 1
            k += 1
        while i < len(left_half):
            arr[k] = left_half[i]
            i += 1
            k += 1
        while j < len(right_half):
            arr[k] = right_half[j]
            j += 1
            k += 1
    return arr
