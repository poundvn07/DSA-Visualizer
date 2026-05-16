"""Các lớp cấu trúc dữ liệu với generator mô phỏng từng bước.

Module này cung cấp 4 cấu trúc dữ liệu tương tác:
- **Stack**: Ngăn xếp (LIFO)
- **Queue**: Hàng đợi (FIFO)
- **LinkedList**: Danh sách liên kết đơn
- **BinarySearchTree**: Cây nhị phân tìm kiếm (BST)

Mỗi thao tác (push, pop, insert, v.v.) là một **Python generator**
sinh ra các đối tượng :class:`~src.core.step.Step` để giao diện
có thể hiển thị hoạt ảnh từng bước.
"""

from __future__ import annotations

from typing import Any, Dict, Generator, List, Optional

from src.core.step import Step


# ──────────────────────────────────────────────────────────────────────
#  Stack (Ngăn xếp — LIFO)
# ──────────────────────────────────────────────────────────────────────

class Stack:
    """Ngăn xếp (Stack) — cấu trúc dữ liệu LIFO (Last In, First Out).

    Phần tử được thêm vào và lấy ra từ **đỉnh** (top) của ngăn xếp.
    Mọi thao tác push/pop đều có độ phức tạp O(1).

    Attributes:
        data: Danh sách lưu các phần tử, ``data[-1]`` là đỉnh stack.
        ops: Bộ đếm tổng số thao tác đã thực hiện.
    """

    def __init__(self) -> None:
        self.data: List[int] = []
        self.ops: int = 0

    def _snap(self, step_type: str, indices: List[int],
              desc: str, hl: int = 0) -> Step:
        """Tạo một bản sao trạng thái hiện tại dưới dạng Step."""
        self.ops += 1
        return Step(
            type=step_type,
            indices=indices,
            array_state=list(self.data),
            description=desc,
            highlight_line=hl,
            comparisons=0,
            swaps=self.ops,
            extra={"ds_type": "stack"},
        )

    def push(self, value: int) -> Generator[Step, None, None]:
        """Thêm phần tử ``value`` vào đỉnh ngăn xếp.

        Args:
            value: Giá trị cần thêm.

        Yields:
            Step: Trạng thái trước và sau khi thêm.
        """
        yield self._snap("highlight", [], f"Preparing to push {value} into stack", 0)
        self.data.append(value)
        idx = len(self.data) - 1
        yield self._snap("push", [idx], f"Pushed {value} to top of stack (index {idx})", 1)

    def pop(self) -> Generator[Step, None, None]:
        """Lấy và xóa phần tử ở đỉnh ngăn xếp.

        Yields:
            Step: Trạng thái trước và sau khi xóa.

        Raises:
            Nếu stack rỗng, sinh ra bước lỗi thay vì ném ngoại lệ.
        """
        if not self.data:
            yield self._snap("not_found", [], "Stack is empty — cannot pop!", 0)
            return
        idx = len(self.data) - 1
        val = self.data[idx]
        yield self._snap("highlight", [idx], f"Preparing to pop {val} from top of stack", 2)
        self.data.pop()
        yield self._snap("pop", [], f"Popped {val} from stack", 3)

    def peek(self) -> Generator[Step, None, None]:
        """Xem phần tử ở đỉnh ngăn xếp mà không xóa.

        Yields:
            Step: Bước đánh dấu phần tử đỉnh.
        """
        if not self.data:
            yield self._snap("not_found", [], "Stack is empty — nothing to peek", 4)
            return
        idx = len(self.data) - 1
        yield self._snap("found", [idx], f"Peek: top of stack = {self.data[idx]}", 4)


# ──────────────────────────────────────────────────────────────────────
#  Queue (Hàng đợi — FIFO)
# ──────────────────────────────────────────────────────────────────────

class Queue:
    """Hàng đợi (Queue) — cấu trúc dữ liệu FIFO (First In, First Out).

    Phần tử được thêm vào **cuối** (rear) và lấy ra từ **đầu** (front).
    Mọi thao tác enqueue/dequeue đều có độ phức tạp O(1) (amortized).

    Attributes:
        data: Danh sách lưu các phần tử, ``data[0]`` là đầu hàng đợi.
        ops: Bộ đếm tổng số thao tác đã thực hiện.
    """

    def __init__(self) -> None:
        self.data: List[int] = []
        self.ops: int = 0

    def _snap(self, step_type: str, indices: List[int],
              desc: str, hl: int = 0) -> Step:
        """Tạo một bản sao trạng thái hiện tại dưới dạng Step."""
        self.ops += 1
        return Step(
            type=step_type,
            indices=indices,
            array_state=list(self.data),
            description=desc,
            highlight_line=hl,
            comparisons=0,
            swaps=self.ops,
            extra={"ds_type": "queue"},
        )

    def enqueue(self, value: int) -> Generator[Step, None, None]:
        """Thêm phần tử ``value`` vào cuối hàng đợi.

        Args:
            value: Giá trị cần thêm.

        Yields:
            Step: Trạng thái trước và sau khi thêm.
        """
        yield self._snap("highlight", [], f"Preparing to enqueue {value}", 0)
        self.data.append(value)
        idx = len(self.data) - 1
        yield self._snap("enqueue", [idx], f"Enqueued {value} to rear of queue", 1)

    def dequeue(self) -> Generator[Step, None, None]:
        """Lấy và xóa phần tử ở đầu hàng đợi.

        Yields:
            Step: Trạng thái trước và sau khi xóa.
        """
        if not self.data:
            yield self._snap("not_found", [], "Queue is empty — cannot dequeue!", 0)
            return
        val = self.data[0]
        yield self._snap("highlight", [0], f"Preparing to dequeue {val} from front", 2)
        self.data.pop(0)
        yield self._snap("dequeue", [], f"Dequeued {val} from queue", 3)

    def peek(self) -> Generator[Step, None, None]:
        """Xem phần tử ở đầu hàng đợi mà không xóa.

        Yields:
            Step: Bước đánh dấu phần tử đầu.
        """
        if not self.data:
            yield self._snap("not_found", [], "Queue is empty — nothing to peek", 4)
            return
        yield self._snap("found", [0], f"Peek: front of queue = {self.data[0]}", 4)


# ──────────────────────────────────────────────────────────────────────
#  Linked List (Danh sách liên kết đơn)
# ──────────────────────────────────────────────────────────────────────

class _LLNode:
    """Nút của danh sách liên kết đơn."""
    __slots__ = ("val", "next")

    def __init__(self, val: int, nxt: Optional[_LLNode] = None):
        self.val = val
        self.next = nxt


class LinkedList:
    """Danh sách liên kết đơn (Singly Linked List).

    Mỗi nút chứa một giá trị và con trỏ đến nút tiếp theo.
    Hỗ trợ: chèn đầu O(1), chèn cuối O(n), xóa O(n), tìm kiếm O(n).

    Attributes:
        head: Con trỏ đến nút đầu tiên (hoặc ``None`` nếu rỗng).
        ops: Bộ đếm tổng số thao tác.
    """

    def __init__(self) -> None:
        self.head: Optional[_LLNode] = None
        self.ops: int = 0

    def _to_list(self) -> List[int]:
        """Chuyển linked list thành danh sách Python."""
        result = []
        cur = self.head
        while cur:
            result.append(cur.val)
            cur = cur.next
        return result

    def _snap(self, step_type: str, indices: List[int],
              desc: str, hl: int = 0) -> Step:
        self.ops += 1
        return Step(
            type=step_type,
            indices=indices,
            array_state=self._to_list(),
            description=desc,
            highlight_line=hl,
            comparisons=0,
            swaps=self.ops,
            extra={"ds_type": "linkedlist"},
        )

    def insert_head(self, value: int) -> Generator[Step, None, None]:
        """Chèn phần tử ``value`` vào đầu danh sách liên kết.

        Độ phức tạp: O(1).

        Args:
            value: Giá trị cần chèn.

        Yields:
            Step: Trạng thái trước và sau khi chèn.
        """
        yield self._snap("highlight", [], f"Create new node with value {value}", 0)
        new_node = _LLNode(value, self.head)
        self.head = new_node
        yield self._snap("insert", [0], f"Inserted {value} at the head of list", 1)

    def insert_tail(self, value: int) -> Generator[Step, None, None]:
        """Chèn phần tử ``value`` vào cuối danh sách liên kết.

        Độ phức tạp: O(n) — cần duyệt đến nút cuối.

        Args:
            value: Giá trị cần chèn.

        Yields:
            Step: Các bước duyệt và chèn.
        """
        yield self._snap("highlight", [], f"Create new node with value {value}", 0)
        new_node = _LLNode(value)
        if self.head is None:
            self.head = new_node
            yield self._snap("insert", [0], f"List is empty — {value} becomes head", 1)
            return

        cur = self.head
        idx = 0
        while cur.next:
            yield self._snap("traverse", [idx], f"Traverse node {cur.val} (index {idx})", 2)
            cur = cur.next
            idx += 1
        cur.next = new_node
        yield self._snap("insert", [idx + 1], f"Inserted {value} at the tail (index {idx + 1})", 3)

    def delete(self, value: int) -> Generator[Step, None, None]:
        """Xóa nút đầu tiên có giá trị ``value``.

        Độ phức tạp: O(n) — cần tìm nút cần xóa.

        Args:
            value: Giá trị cần xóa.

        Yields:
            Step: Các bước tìm kiếm và xóa.
        """
        if self.head is None:
            yield self._snap("not_found", [], "List is empty — cannot delete", 0)
            return

        if self.head.val == value:
            yield self._snap("found", [0], f"Found {value} at head (index 0)", 4)
            self.head = self.head.next
            yield self._snap("delete", [], f"Deleted {value} from list", 5)
            return

        cur = self.head
        idx = 0
        while cur.next:
            yield self._snap("traverse", [idx], f"Traverse node {cur.val} (index {idx})", 4)
            if cur.next.val == value:
                yield self._snap("found", [idx + 1], f"Found {value} at index {idx + 1}", 4)
                cur.next = cur.next.next
                yield self._snap("delete", [], f"Deleted {value} from list", 5)
                return
            cur = cur.next
            idx += 1
        yield self._snap("not_found", [], f"Could not find {value} in the list", 6)

    def search(self, value: int) -> Generator[Step, None, None]:
        """Tìm kiếm nút có giá trị ``value``.

        Độ phức tạp: O(n).

        Args:
            value: Giá trị cần tìm.

        Yields:
            Step: Các bước duyệt và kết quả tìm kiếm.
        """
        cur = self.head
        idx = 0
        while cur:
            yield self._snap("compare", [idx], f"Compare node[{idx}]={cur.val} with {value}", 7)
            if cur.val == value:
                yield self._snap("found", [idx], f"Found {value} at index {idx}!", 8)
                return
            cur = cur.next
            idx += 1
        yield self._snap("not_found", [], f"Could not find {value} in the list", 9)


# ──────────────────────────────────────────────────────────────────────
#  Binary Search Tree (Cây nhị phân tìm kiếm)
# ──────────────────────────────────────────────────────────────────────

class _BSTNode:
    """Nút của cây nhị phân tìm kiếm."""
    __slots__ = ("val", "left", "right")

    def __init__(self, val: int):
        self.val = val
        self.left: Optional[_BSTNode] = None
        self.right: Optional[_BSTNode] = None


class BinarySearchTree:
    """Cây nhị phân tìm kiếm (Binary Search Tree — BST).

    Mỗi nút trái có giá trị nhỏ hơn nút cha, mỗi nút phải có giá trị
    lớn hơn. Hỗ trợ: insert O(log n) trung bình, search O(log n),
    duyệt inorder O(n).

    Attributes:
        root: Nút gốc của cây (hoặc ``None`` nếu cây rỗng).
        ops: Bộ đếm tổng số thao tác.
    """

    def __init__(self) -> None:
        self.root: Optional[_BSTNode] = None
        self.ops: int = 0

    def _to_list(self) -> List[int]:
        """Chuyển BST thành danh sách theo thứ tự inorder."""
        result: List[int] = []
        def _inorder(node: Optional[_BSTNode]) -> None:
            if node:
                _inorder(node.left)
                result.append(node.val)
                _inorder(node.right)
        _inorder(self.root)
        return result

    def _tree_layout(self) -> Dict[str, Any]:
        """Tạo dữ liệu bố cục cây để renderer vẽ.

        Returns:
            Dict với ``nodes`` (danh sách nút có tọa độ) và ``edges``
            (danh sách cạnh nối giữa các nút).
        """
        if self.root is None:
            return {"nodes": [], "edges": []}

        nodes: List[Dict[str, Any]] = []
        edges: List[Dict[str, int]] = []
        node_id = 0

        def _layout(node: Optional[_BSTNode], depth: int,
                     pos: float, spread: float,
                     parent_id: int = -1) -> None:
            nonlocal node_id
            if node is None:
                return
            my_id = node_id
            node_id += 1
            nodes.append({
                "id": my_id, "val": node.val,
                "x": pos, "y": depth, "highlight": "",
            })
            if parent_id >= 0:
                edges.append({"from": parent_id, "to": my_id})
            _layout(node.left, depth + 1, pos - spread, spread / 2, my_id)
            _layout(node.right, depth + 1, pos + spread, spread / 2, my_id)

        _layout(self.root, 0, 0.5, 0.25)
        return {"nodes": nodes, "edges": edges}

    def _snap(self, step_type: str, indices: List[int],
              desc: str, hl: int = 0,
              highlight_vals: Optional[List[int]] = None) -> Step:
        self.ops += 1
        layout = self._tree_layout()
        if highlight_vals:
            for n in layout["nodes"]:
                if n["val"] in highlight_vals:
                    n["highlight"] = step_type
        return Step(
            type=step_type,
            indices=indices,
            array_state=self._to_list(),
            description=desc,
            highlight_line=hl,
            comparisons=0,
            swaps=self.ops,
            extra={"ds_type": "bst", "tree": layout},
        )

    def insert(self, value: int) -> Generator[Step, None, None]:
        """Chèn giá trị ``value`` vào BST.

        Đi từ gốc, rẽ trái nếu ``value`` nhỏ hơn nút hiện tại,
        rẽ phải nếu lớn hơn, cho đến khi tìm được vị trí trống.

        Độ phức tạp: O(log n) trung bình, O(n) trường hợp xấu nhất.

        Args:
            value: Giá trị cần chèn.

        Yields:
            Step: Các bước duyệt cây và chèn.
        """
        if self.root is None:
            self.root = _BSTNode(value)
            yield self._snap("insert", [], f"Tree is empty — {value} becomes root",
                             0, [value])
            return

        path: List[int] = []
        cur = self.root
        while True:
            path.append(cur.val)
            yield self._snap("compare", [], f"Compare {value} with node {cur.val}",
                             1, [cur.val])
            if value < cur.val:
                if cur.left is None:
                    cur.left = _BSTNode(value)
                    yield self._snap("insert", [],
                                     f"Insert {value} as left child of {cur.val}",
                                     2, [value])
                    return
                cur = cur.left
            elif value > cur.val:
                if cur.right is None:
                    cur.right = _BSTNode(value)
                    yield self._snap("insert", [],
                                     f"Insert {value} as right child of {cur.val}",
                                     3, [value])
                    return
                cur = cur.right
            else:
                yield self._snap("found", [],
                                 f"Value {value} already exists — skipping",
                                 4, [value])
                return

    def search(self, value: int) -> Generator[Step, None, None]:
        """Tìm kiếm giá trị ``value`` trong BST.

        Đi từ gốc, rẽ trái/phải dựa trên so sánh.

        Độ phức tạp: O(log n) trung bình.

        Args:
            value: Giá trị cần tìm.

        Yields:
            Step: Các bước duyệt và kết quả tìm kiếm.
        """
        cur = self.root
        if cur is None:
            yield self._snap("not_found", [], "Tree is empty — not found", 5)
            return

        while cur:
            yield self._snap("compare", [], f"Compare {value} with node {cur.val}",
                             6, [cur.val])
            if value == cur.val:
                yield self._snap("found", [], f"Found {value}!", 7, [cur.val])
                return
            elif value < cur.val:
                yield self._snap("traverse", [],
                                 f"{value} < {cur.val} → go left", 8, [cur.val])
                cur = cur.left
            else:
                yield self._snap("traverse", [],
                                 f"{value} > {cur.val} → go right", 9, [cur.val])
                cur = cur.right
        yield self._snap("not_found", [], f"Could not find {value} in BST", 10)

    def inorder(self) -> Generator[Step, None, None]:
        """Duyệt cây theo thứ tự inorder (trái → gốc → phải).

        Kết quả duyệt inorder của BST luôn là dãy đã sắp xếp tăng dần.

        Yields:
            Step: Mỗi bước tương ứng với một nút được thăm.
        """
        visited: List[int] = []

        def _walk(node: Optional[_BSTNode]) -> Generator[Step, None, None]:
            if node is None:
                return
            yield from _walk(node.left)
            visited.append(node.val)
            yield self._snap("traverse", [],
                             f"Visit node {node.val} (inorder)", 11, [node.val])
            yield from _walk(node.right)

        if self.root is None:
            yield self._snap("not_found", [], "Tree is empty — nothing to traverse", 11)
            return
        yield from _walk(self.root)
        yield self._snap("found", [], f"Inorder traversal complete: {visited}", 11, visited)


# ──────────────────────────────────────────────────────────────────────
#  Hàm tiện ích: chạy chuỗi thao tác trên DS
# ──────────────────────────────────────────────────────────────────────

def run_ds_operations(
    ds_type: str,
    operations: List[Dict[str, Any]],
) -> Generator[Step, None, None]:
    """Chạy một chuỗi thao tác trên cấu trúc dữ liệu đã chọn.

    Hàm này tạo một instance DS mới, rồi thực hiện lần lượt từng thao
    tác trong danh sách ``operations``. Mỗi thao tác là một dict có
    dạng ``{"op": "push", "value": 42}`` hoặc ``{"op": "pop"}``.

    Args:
        ds_type: Loại cấu trúc dữ liệu — ``"stack"``, ``"queue"``,
            ``"linkedlist"``, hoặc ``"bst"``.
        operations: Danh sách các thao tác cần thực hiện.

    Yields:
        Step: Tất cả các bước mô phỏng cho toàn bộ chuỗi thao tác.

    Example::

        ops = [{"op": "push", "value": 10}, {"op": "push", "value": 20}]
        for step in run_ds_operations("stack", ops):
            print(step.description)
    """
    if ds_type == "stack":
        ds = Stack()
        for o in operations:
            op = o["op"]
            if op == "push":
                yield from ds.push(o["value"])
            elif op == "pop":
                yield from ds.pop()
            elif op == "peek":
                yield from ds.peek()

    elif ds_type == "queue":
        ds = Queue()
        for o in operations:
            op = o["op"]
            if op == "enqueue":
                yield from ds.enqueue(o["value"])
            elif op == "dequeue":
                yield from ds.dequeue()
            elif op == "peek":
                yield from ds.peek()

    elif ds_type == "linkedlist":
        ds = LinkedList()
        for o in operations:
            op = o["op"]
            if op == "insert_head":
                yield from ds.insert_head(o["value"])
            elif op == "insert_tail":
                yield from ds.insert_tail(o["value"])
            elif op == "delete":
                yield from ds.delete(o["value"])
            elif op == "search":
                yield from ds.search(o["value"])

    elif ds_type == "bst":
        ds = BinarySearchTree()
        for o in operations:
            op = o["op"]
            if op == "insert":
                yield from ds.insert(o["value"])
            elif op == "search":
                yield from ds.search(o["value"])
            elif op == "inorder":
                yield from ds.inorder()
