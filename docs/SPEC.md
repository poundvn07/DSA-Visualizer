# SPEC.md — Algorithm Visualizer & Benchmarking Specification

## 1. Algorithms

### 1.1 Sorting — O(n log n)

| Algorithm  | Variant          | Key Operations Visualized                |
|------------|-----------------|------------------------------------------|
| QuickSort  | Lomuto partition | Pivot selection, compare, swap, partition |
| HeapSort   | Max-heap         | Heapify (sift-down), extract-max, swap   |
| MergeSort  | Top-down         | Split, merge, element placement           |

### 1.2 Searching — O(log n)

| Algorithm     | Precondition   | Key Operations Visualized         |
|---------------|---------------|-----------------------------------|
| Binary Search | Sorted array  | Range narrowing [low, mid, high]  |

## 2. Data Structures

- **Array / List** — random-access, in-place swap for visualization.
  The same Python `list[int]` is used by every algorithm; copies are
  made before mutation so the original is never corrupted.

## 3. UI Layout

The window is divided into **4 logical panels**:

```
┌─────────────────────────────────────────────────────────┐
│ [1] CONFIGURATION │  [2] MAIN VISUALIZATION AREA        │
│-------------------│                                     │
│ Type: Sorting /   │  Animated bars representing array   │
│       Searching   │  Status label: e.g.                 │
│                   │  "Comparing arr[2] and arr[5]"      │
│ Algorithm: <drop> │                                     │
│                   │─────────────────────────────────────│
│ Array Size (N):   │  [3] CONTROL & INFO BAR             │
│ <----50------>    │                                     │
│                   │  [New]  [<< Step]  [▶ Play]         │
│ Speed:            │  [Step >>]  [Reset]                 │
│ <----Fast---->    │                                     │
│ Input Type:       │  Pseudo-code  │  Live Stats         │
│ ( ) Random        │  (highlighted │  Algorithm: Quick   │
│ ( ) Sorted        │   per step)   │  N: 50              │
│ ( ) Reversed      │               │  Comparisons: 125   │
│───────────────────│               │  Swaps: 68          │
│ [4] EXTRA PANEL   │─────────────────────────────────────│
│ [>> Benchmark]    │                                     │
│ [?]  Help         │                                     │
└─────────────────────────────────────────────────────────┘
```

### Panel Descriptions

| # | Panel                   | Responsibility |
|---|-------------------------|----------------|
| 1 | **Configuration**       | Algorithm type toggle (Sorting / Searching), algorithm dropdown, array-size slider (5–200), speed slider (1–500 ms), input-type radio buttons (Random / Sorted / Reversed). |
| 2 | **Visualization Area**  | Tkinter Canvas rendering vertical bars proportional to element value. Color-coded by current step type. Status label below bars. |
| 3 | **Control & Info Bar**  | Transport buttons: New, << Step, ▶ Play, Step >>, Reset. Below: side-by-side Pseudo-code panel and Stats panel. |
| 4 | **Extra Panel**         | [>> Benchmark] button launches benchmark in daemon thread. [?] Help button shows usage dialog. |

## 4. Color Coding

| State     | Color   | Hex       |
|-----------|---------|-----------|
| Default   | Blue    | `#3B82F6` |
| Comparing | Yellow  | `#FACC15` |
| Swap      | Red     | `#EF4444` |
| Pivot     | Orange  | `#F97316` |
| Found     | Green   | `#22C55E` |
| Set       | Purple  | `#A855F7` |
| Range     | Cyan    | `#06B6D4` |

## 5. Architecture Rules

### Directory Layout

```
src/
├── core/
│   ├── __init__.py
│   ├── step.py              # Step dataclass
│   ├── algorithms.py        # Algorithm generator functions
│   └── pseudocode.py        # Pseudo-code line mappings
├── ui/
│   ├── __init__.py
│   ├── main_window.py       # Top-level window assembly
│   ├── visualization_canvas.py
│   ├── config_panel.py
│   ├── control_panel.py
│   ├── stats_panel.py
│   └── pseudocode_panel.py
├── benchmarking/
│   ├── __init__.py
│   ├── data_generator.py
│   └── benchmark_runner.py
└── utils/
    ├── __init__.py
    └── helpers.py
```

### Invariants

1. All algorithms are **generators** that `yield Step`.
2. `Step.array_state` is always a **snapshot** (shallow copy) of the
   current array — never a reference to the mutable working copy.
3. The GUI **never blocks** the main thread; `widget.after()` drives
   animation; benchmarks run in `threading.Thread(daemon=True)`.
4. Every public class and function carries a **Google-style docstring**
   with `Args`, `Returns` / `Yields`, and `Raises` sections.

## 6. Benchmarking Specification

| Parameter      | Value             |
|----------------|-------------------|
| Array size     | 1 000 000         |
| Repetitions    | 10 per algorithm  |
| Timing         | `time.perf_counter()` |
| Algorithms     | QuickSort, HeapSort, MergeSort |

### Output Format

```
Running QuickSort
  [1/10] : 377.64 ms
  [2/10] : 393.55 ms
  ...
  [10/10]: 770.95 ms
```

## 7. Entry Points

| Command                              | Action                     |
|--------------------------------------|----------------------------|
| `python main.py`                     | Launch GUI                 |
| `python -m src.benchmarking.benchmark_runner` | Run CLI benchmarks |
