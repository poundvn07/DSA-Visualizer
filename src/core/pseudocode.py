"""File này lưu giả mã cho thuật toán và cấu trúc dữ liệu.

Giao diện dùng danh sách này để tô sáng dòng đang chạy.
"""

from __future__ import annotations

from typing import Dict, List

# Mapping: algorithm name → ordered list of pseudo-code lines.
PSEUDOCODE: Dict[str, List[str]] = {

    # ── QuickSort (Lomuto) ────────────────────────────────────────
    "QuickSort": [
        "function quickSort(arr, low, high):",
        "    pivot ← arr[high]",
        "    i ← low - 1",
        "    for j ← low to high - 1:",
        "        if arr[j] ≤ pivot:",
        "            i ← i + 1; swap(arr[i], arr[j])",
        "    end for",
        "    swap(arr[i+1], arr[high])        // place pivot",
        "    return i + 1",
        "    quickSort(arr, low, pi - 1)",
        "    quickSort(arr, pi + 1, high)",
    ],

    # ── HeapSort ──────────────────────────────────────────────────
    "HeapSort": [
        "function heapSort(arr):",
        "    buildMaxHeap(arr)",
        "    function siftDown(start, end):",
        "        child ← 2·start + 1",
        "        if right child > left child: child ← right",
        "        if arr[root] < arr[child]:",
        "            swap(arr[root], arr[child])",
        "            root ← child",
        "    // Build heap from last parent to root",
        "    for end ← n-1 down to 1:",
        "        swap(arr[0], arr[end])        // extract max",
        "        siftDown(0, end - 1)",
    ],

    # ── MergeSort ─────────────────────────────────────────────────
    "MergeSort": [
        "function mergeSort(arr, left, right):",
        "    mid ← (left + right) / 2",
        "    mergeSort(arr, left, mid)",
        "    mergeSort(arr, mid+1, right)",
        "    // merge step:",
        "    while i ≤ mid and j ≤ right:",
        "        if arr[i] ≤ arr[j]: take left",
        "        else: take right",
        "    place merged element back into arr[k]",
    ],

    # ── Binary Search ─────────────────────────────────────────────
    "BinarySearch": [
        "function binarySearch(arr, target):",
        "    low ← 0; high ← n - 1",
        "    while low ≤ high:",
        "        mid ← (low + high) / 2",
        "        if arr[mid] = target: return mid   // found!",
        "        else if arr[mid] < target:",
        "            low ← mid + 1                  // right half",
        "        else:",
        "            high ← mid - 1                 // left half",
        "    return -1                                // not found",
        "    // target is not in the array",
    ],

    # ── Stack ─────────────────────────────────────────────────────
    "Stack": [
        "function push(value):",
        "    stack.append(value)          // thêm vào đỉnh",
        "function pop():",
        "    if stack is empty: ERROR",
        "    return stack.removeLast()    // xóa đỉnh",
        "function peek():",
        "    return stack[top]            // xem đỉnh",
    ],

    # ── Queue ─────────────────────────────────────────────────────
    "Queue": [
        "function enqueue(value):",
        "    queue.append(value)          // thêm vào cuối",
        "function dequeue():",
        "    if queue is empty: ERROR",
        "    return queue.removeFirst()   // xóa đầu",
        "function peek():",
        "    return queue[front]          // xem đầu",
    ],

    # ── Linked List ───────────────────────────────────────────────
    "LinkedList": [
        "function insertHead(value):",
        "    newNode.next ← head; head ← newNode",
        "function insertTail(value):",
        "    traverse to last node",
        "    lastNode.next ← newNode",
        "function delete(value):",
        "    traverse to find node",
        "    prevNode.next ← node.next   // bỏ qua nút",
        "function search(value):",
        "    cur ← head",
        "    while cur ≠ null:",
        "        if cur.val = value: return FOUND",
        "        cur ← cur.next",
    ],

    # ── Binary Search Tree ────────────────────────────────────────
    "BST": [
        "function insert(value):",
        "    if tree is empty: root ← newNode(value)",
        "    if value < node.val: go LEFT",
        "    if value > node.val: go RIGHT",
        "    if value = node.val: DUPLICATE",
        "function search(value):",
        "    cur ← root",
        "    if value = cur.val: return FOUND",
        "    if value < cur.val: cur ← cur.left",
        "    if value > cur.val: cur ← cur.right",
        "    return NOT_FOUND",
        "function inorder(node):",
        "    inorder(node.left); visit(node); inorder(node.right)",
    ],
}

def get_pseudocode(algorithm_name: str) -> List[str]:
    """Lấy giả mã theo tên thuật toán hoặc cấu trúc dữ liệu.
    
    Args:
        algorithm_name: Tên cần tìm trong PSEUDOCODE.
    
    Return:
        Danh sách các dòng giả mã.
    """
    return PSEUDOCODE[algorithm_name]