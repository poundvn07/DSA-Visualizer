"""File này định nghĩa lớp Step.

Step là một bước nhỏ trong lúc mô phỏng thuật toán hoặc cấu trúc dữ liệu.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Step:
    """Lớp lưu thông tin của một bước mô phỏng.
    
    Attributes:
        type: Loại bước, ví dụ compare hoặc swap.
        indices: Các vị trí liên quan đến bước này.
        array_state: Trạng thái mảng tại bước này.
        description: Nội dung mô tả ngắn.
        highlight_line: Dòng giả mã cần tô sáng.
        comparisons: Tổng số lần so sánh.
        swaps: Tổng số lần đổi chỗ hoặc ghi.
        extra: Thông tin phụ cho giao diện.
    """

    type: str
    indices: List[int]
    array_state: List[int]
    description: str
    highlight_line: int = 0
    comparisons: int = 0
    swaps: int = 0
    extra: Optional[Dict[str, Any]] = field(default=None, repr=False)
