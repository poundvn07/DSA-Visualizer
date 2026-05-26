"""File này chứa các cấu trúc dữ liệu để mô phỏng.

Các thao tác như push, pop, enqueue, insert hoặc search sẽ tạo ra từng Step cho giao diện.
"""

from __future__ import annotations

from typing import Any, Dict, Generator, List, Optional

from src.core.step import Step


class Stack:
    """Lớp mô phỏng Stack.
    
    Stack hoạt động theo kiểu vào sau ra trước.
    """

    def __init__(self) -> None:
        self.data: List[int] = []
        self.ops = 0

    def _snap(self, step_type: str, indices: List[int],
              desc: str, hl: int = 0) -> Step:
        """Tạo Step từ trạng thái hiện tại của Stack.
        
        Args:
            step_type: Loại bước.
            indices: Các vị trí cần tô sáng.
            desc: Mô tả của bước.
            hl: Dòng giả mã cần tô sáng.
        
        Return:
            Một Step mới.
        """
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
        """Thêm một giá trị vào đỉnh Stack.
        
        Args:
            value: Giá trị cần thêm.
        
        Yield:
            Step: Các bước trước và sau khi thêm.
        """
        yield self._snap("highlight", [], f"Preparing to push {value} into stack", 0)
        self.data.append(value)
        index = len(self.data) - 1
        yield self._snap("push", [index], f"Pushed {value} to top of stack (index {index})", 1)

    def pop(self) -> Generator[Step, None, None]:
        """Lấy phần tử ở đỉnh Stack ra.
        
        Yield:
            Step: Các bước trước và sau khi lấy phần tử.
        """
        if not self.data:
            yield self._snap("not_found", [], "Stack is empty — cannot pop!", 0)
            return

        index = len(self.data) - 1
        value = self.data[index]
        yield self._snap("highlight", [index], f"Preparing to pop {value} from top of stack", 2)
        self.data.pop()
        yield self._snap("pop", [], f"Popped {value} from stack", 3)

    def peek(self) -> Generator[Step, None, None]:
        """Xem phần tử ở đỉnh Stack mà không xóa.
        
        Yield:
            Step: Bước hiển thị phần tử ở đỉnh.
        """
        if not self.data:
            yield self._snap("not_found", [], "Stack is empty — nothing to peek", 4)
            return

        index = len(self.data) - 1
        yield self._snap("found", [index], f"Peek: top of stack = {self.data[index]}", 4)


class Queue:
    """Lớp mô phỏng Queue.
    
    Queue hoạt động theo kiểu vào trước ra trước.
    """

    def __init__(self) -> None:
        self.data: List[int] = []
        self.ops = 0

    def _snap(self, step_type: str, indices: List[int],
              desc: str, hl: int = 0) -> Step:
        """Tạo Step từ trạng thái hiện tại của Queue.
        
        Args:
            step_type: Loại bước.
            indices: Các vị trí cần tô sáng.
            desc: Mô tả của bước.
            hl: Dòng giả mã cần tô sáng.
        
        Return:
            Một Step mới.
        """
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
        """Thêm một giá trị vào cuối Queue.
        
        Args:
            value: Giá trị cần thêm.
        
        Yield:
            Step: Các bước trước và sau khi thêm.
        """
        yield self._snap("highlight", [], f"Preparing to enqueue {value}", 0)
        self.data.append(value)
        index = len(self.data) - 1
        yield self._snap("enqueue", [index], f"Enqueued {value} to rear of queue", 1)

    def dequeue(self) -> Generator[Step, None, None]:
        """Lấy phần tử ở đầu Queue ra.
        
        Yield:
            Step: Các bước trước và sau khi lấy phần tử.
        """
        if not self.data:
            yield self._snap("not_found", [], "Queue is empty — cannot dequeue!", 0)
            return

        value = self.data[0]
        yield self._snap("highlight", [0], f"Preparing to dequeue {value} from front", 2)
        self.data.pop(0)
        yield self._snap("dequeue", [], f"Dequeued {value} from queue", 3)

    def peek(self) -> Generator[Step, None, None]:
        """Xem phần tử ở đầu Queue mà không xóa.
        
        Yield:
            Step: Bước hiển thị phần tử ở đầu.
        """
        if not self.data:
            yield self._snap("not_found", [], "Queue is empty — nothing to peek", 4)
            return

        yield self._snap("found", [0], f"Peek: front of queue = {self.data[0]}", 4)


class _LLNode:
    """Lớp nút dùng cho LinkedList.
    
    Attributes:
        val: Giá trị của nút.
        next: Nút tiếp theo.
    """
    __slots__ = ("val", "next")

    def __init__(self, val: int, nxt: Optional[_LLNode] = None):
        self.val = val
        self.next = nxt


class LinkedList:
    """Lớp mô phỏng danh sách liên kết đơn.
    
    Mỗi nút giữ một giá trị và liên kết tới nút tiếp theo.
    """

    def __init__(self) -> None:
        self.head: Optional[_LLNode] = None
        self.ops = 0

    def _to_list(self) -> List[int]:
        """Chuyển LinkedList thành list thường.
        
        Return:
            Danh sách các giá trị hiện có.
        """
        result: List[int] = []
        current = self.head
        while current is not None:
            result.append(current.val)
            current = current.next
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
        """Thêm một giá trị vào đầu LinkedList.
        
        Args:
            value: Giá trị cần thêm.
        
        Yield:
            Step: Các bước trước và sau khi thêm.
        """
        yield self._snap("highlight", [], f"Create new node with value {value}", 0)
        self.head = _LLNode(value, self.head)
        yield self._snap("insert", [0], f"Inserted {value} at the head of list", 1)

    def insert_tail(self, value: int) -> Generator[Step, None, None]:
        """Thêm một giá trị vào cuối LinkedList.
        
        Args:
            value: Giá trị cần thêm.
        
        Yield:
            Step: Các bước duyệt và thêm nút.
        """
        yield self._snap("highlight", [], f"Create new node with value {value}", 0)
        new_node = _LLNode(value)

        if self.head is None:
            self.head = new_node
            yield self._snap("insert", [0], f"List is empty — {value} becomes head", 1)
            return

        current = self.head
        index = 0
        while current.next is not None:
            yield self._snap("traverse", [index], f"Traverse node {current.val} (index {index})", 2)
            current = current.next
            index += 1

        current.next = new_node
        yield self._snap("insert", [index + 1], f"Inserted {value} at the tail (index {index + 1})", 3)

    def delete(self, value: int) -> Generator[Step, None, None]:
        """Xóa nút đầu tiên có giá trị cần tìm.
        
        Args:
            value: Giá trị cần xóa.
        
        Yield:
            Step: Các bước tìm và xóa nút.
        """
        if self.head is None:
            yield self._snap("not_found", [], "List is empty — cannot delete", 0)
            return

        if self.head.val == value:
            yield self._snap("found", [0], f"Found {value} at head (index 0)", 4)
            self.head = self.head.next
            yield self._snap("delete", [], f"Deleted {value} from list", 5)
            return

        current = self.head
        index = 0
        while current.next is not None:
            yield self._snap("traverse", [index], f"Traverse node {current.val} (index {index})", 4)
            if current.next.val == value:
                yield self._snap("found", [index + 1], f"Found {value} at index {index + 1}", 4)
                current.next = current.next.next
                yield self._snap("delete", [], f"Deleted {value} from list", 5)
                return
            current = current.next
            index += 1

        yield self._snap("not_found", [], f"Could not find {value} in the list", 6)

    def search(self, value: int) -> Generator[Step, None, None]:
        """Tìm một giá trị trong LinkedList.
        
        Args:
            value: Giá trị cần tìm.
        
        Yield:
            Step: Các bước so sánh và kết quả tìm kiếm.
        """
        current = self.head
        index = 0
        while current is not None:
            yield self._snap("compare", [index], f"Compare node[{index}]={current.val} with {value}", 7)
            if current.val == value:
                yield self._snap("found", [index], f"Found {value} at index {index}!", 8)
                return
            current = current.next
            index += 1

        yield self._snap("not_found", [], f"Could not find {value} in the list", 9)


class _BSTNode:
    """Lớp nút dùng cho cây BST.
    
    Attributes:
        val: Giá trị của nút.
        left: Nút con bên trái.
        right: Nút con bên phải.
    """
    __slots__ = ("val", "left", "right")

    def __init__(self, val: int):
        self.val = val
        self.left: Optional[_BSTNode] = None
        self.right: Optional[_BSTNode] = None


class BinarySearchTree:
    """Lớp mô phỏng cây tìm kiếm nhị phân.
    
    Giá trị nhỏ hơn nằm bên trái, giá trị lớn hơn nằm bên phải.
    """

    def __init__(self) -> None:
        self.root: Optional[_BSTNode] = None
        self.ops = 0

    def _to_list(self) -> List[int]:
        """Chuyển BST thành list theo thứ tự inorder.
        
        Return:
            Danh sách giá trị đã được duyệt inorder.
        """
        result: List[int] = []

        def _inorder(node: Optional[_BSTNode]) -> None:
            if node is None:
                return
            _inorder(node.left)
            result.append(node.val)
            _inorder(node.right)

        _inorder(self.root)
        return result

    def _tree_layout(self) -> Dict[str, Any]:
        """Tạo dữ liệu vị trí để vẽ cây.
        
        Return:
            Dict gồm danh sách nút và cạnh của cây.
        """
        nodes: List[Dict[str, Any]] = []
        edges: List[Dict[str, int]] = []
        next_id = 0

        def _layout(node: Optional[_BSTNode], depth: int,
                    pos: float, spread: float,
                    parent_id: int = -1) -> None:
            nonlocal next_id
            if node is None:
                return

            my_id = next_id
            next_id += 1
            nodes.append({
                "id": my_id,
                "val": node.val,
                "x": pos,
                "y": depth,
                "highlight": "",
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
            for node in layout["nodes"]:
                if node["val"] in highlight_vals:
                    node["highlight"] = step_type

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
        """Thêm một giá trị vào BST.
        
        Args:
            value: Giá trị cần thêm.
        
        Yield:
            Step: Các bước duyệt và thêm nút.
        """
        if self.root is None:
            self.root = _BSTNode(value)
            yield self._snap("insert", [], f"Tree is empty — {value} becomes root", 0, [value])
            return

        current = self.root
        while True:
            yield self._snap("compare", [], f"Compare {value} with node {current.val}", 1, [current.val])
            if value < current.val:
                if current.left is None:
                    current.left = _BSTNode(value)
                    yield self._snap("insert", [], f"Insert {value} as left child of {current.val}", 2, [value])
                    return
                current = current.left
            elif value > current.val:
                if current.right is None:
                    current.right = _BSTNode(value)
                    yield self._snap("insert", [], f"Insert {value} as right child of {current.val}", 3, [value])
                    return
                current = current.right
            else:
                yield self._snap("found", [], f"Value {value} already exists — skipping", 4, [value])
                return

    def search(self, value: int) -> Generator[Step, None, None]:
        """Tìm một giá trị trong BST.
        
        Args:
            value: Giá trị cần tìm.
        
        Yield:
            Step: Các bước duyệt và kết quả tìm kiếm.
        """
        current = self.root
        if current is None:
            yield self._snap("not_found", [], "Tree is empty — not found", 5)
            return

        while current is not None:
            yield self._snap("compare", [], f"Compare {value} with node {current.val}", 6, [current.val])
            if value == current.val:
                yield self._snap("found", [], f"Found {value}!", 7, [current.val])
                return
            if value < current.val:
                yield self._snap("traverse", [], f"{value} < {current.val} → go left", 8, [current.val])
                current = current.left
            else:
                yield self._snap("traverse", [], f"{value} > {current.val} → go right", 9, [current.val])
                current = current.right

        yield self._snap("not_found", [], f"Could not find {value} in BST", 10)

    def inorder(self) -> Generator[Step, None, None]:
        """Duyệt BST theo thứ tự trái, gốc, phải.
        
        Yield:
            Step: Các bước thăm từng nút.
        """
        if self.root is None:
            yield self._snap("not_found", [], "Tree is empty — nothing to traverse", 11)
            return

        visited: List[int] = []

        def _walk(node: Optional[_BSTNode]) -> Generator[Step, None, None]:
            if node is None:
                return
            yield from _walk(node.left)
            visited.append(node.val)
            yield self._snap("traverse", [], f"Visit node {node.val} (inorder)", 11, [node.val])
            yield from _walk(node.right)

        yield from _walk(self.root)
        yield self._snap("found", [], f"Inorder traversal complete: {visited}", 11, visited)


def run_ds_operations(
    ds_type: str,
    operations: List[Dict[str, Any]],
) -> Generator[Step, None, None]:
    """Chạy lần lượt các thao tác trên cấu trúc dữ liệu.
    
    Args:
        ds_type: Loại cấu trúc dữ liệu.
        operations: Danh sách thao tác cần chạy.
    
    Yield:
        Step: Các bước mô phỏng của toàn bộ thao tác.
    """
    if ds_type == "stack":
        ds = Stack()
        for item in operations:
            op = item["op"]
            if op == "push":
                yield from ds.push(item["value"])
            elif op == "pop":
                yield from ds.pop()
            elif op == "peek":
                yield from ds.peek()

    elif ds_type == "queue":
        ds = Queue()
        for item in operations:
            op = item["op"]
            if op == "enqueue":
                yield from ds.enqueue(item["value"])
            elif op == "dequeue":
                yield from ds.dequeue()
            elif op == "peek":
                yield from ds.peek()

    elif ds_type == "linkedlist":
        ds = LinkedList()
        for item in operations:
            op = item["op"]
            if op == "insert_head":
                yield from ds.insert_head(item["value"])
            elif op == "insert_tail":
                yield from ds.insert_tail(item["value"])
            elif op == "delete":
                yield from ds.delete(item["value"])
            elif op == "search":
                yield from ds.search(item["value"])

    elif ds_type == "bst":
        ds = BinarySearchTree()
        for item in operations:
            op = item["op"]
            if op == "insert":
                yield from ds.insert(item["value"])
            elif op == "search":
                yield from ds.search(item["value"])
            elif op == "inorder":
                yield from ds.inorder()
