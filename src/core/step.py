"""Dataclass Step cho việc mô phỏng thuật toán và cấu trúc dữ liệu.

Module này định nghĩa lớp ``Step`` dùng làm đơn vị giao tiếp chung
giữa các hàm generator (thuật toán / cấu trúc dữ liệu) và giao diện.
Mỗi generator sẽ sinh ra (yield) các đối tượng ``Step`` mô tả một thao
tác nguyên tử (so sánh, hoán đổi, push, pop, insert, v.v.) cùng với
một **bản sao** trạng thái tại thời điểm đó.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Step:
    """Bản ghi bất biến của một thao tác nguyên tử.

    Attributes:
        type: Loại thao tác. Ví dụ: ``"compare"``, ``"swap"``,
            ``"set"``, ``"pivot"``, ``"found"``, ``"not_found"``,
            ``"range"``, ``"push"``, ``"pop"``, ``"enqueue"``,
            ``"dequeue"``, ``"insert"``, ``"delete"``, ``"search"``,
            ``"traverse"``.
        indices: Các vị trí (chỉ mục) liên quan đến thao tác này.
        array_state: Một **bản sao** (shallow copy) của danh sách/mảng
            **sau** khi thao tác đã được thực hiện. Giao diện sẽ đọc
            trường này để vẽ lại thanh biểu đồ hoặc các phần tử DS.
        description: Câu mô tả ngắn hiển thị trên thanh trạng thái,
            ví dụ ``"So sánh arr[2] và arr[5]"``.
        highlight_line: Chỉ mục (bắt đầu từ 0) vào danh sách
            pseudo-code cần được đánh dấu khi bước này hiển thị.
        comparisons: Tổng số lần so sánh tính đến bước này.
        swaps: Tổng số lần hoán đổi / thao tác ghi tính đến bước này.
        extra: Dữ liệu bổ sung dành cho cấu trúc dữ liệu. Ví dụ:
            danh sách nút cây (BST), mũi tên liên kết (Linked List),
            v.v. Mặc định là ``None`` (các thuật toán sắp xếp/tìm kiếm
            không sử dụng trường này).

    Example::

        step = Step(
            type="push",
            indices=[3],
            array_state=[10, 20, 30, 40],
            description="Push 40 vào đỉnh stack",
            extra={"ds_type": "stack"},
        )
    """

    type: str
    indices: List[int]
    array_state: List[int]
    description: str
    highlight_line: int = 0
    comparisons: int = 0
    swaps: int = 0
    extra: Optional[Dict[str, Any]] = field(default=None, repr=False)
