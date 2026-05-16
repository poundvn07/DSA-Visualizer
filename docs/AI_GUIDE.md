# AI_GUIDE.md — Algorithm Visualizer & Benchmarking

## Tech Stack

| Layer         | Technology                                      |
|---------------|------------------------------------------------|
| Language      | Python 3.10+                                   |
| UI Framework  | [Eel](https://github.com/python-eel/Eel) — Python ↔ JS bridge |
| Frontend      | Vanilla HTML5 / CSS3 / JavaScript (Canvas API) |
| Benchmarking  | `time.perf_counter()` for sub-millisecond precision |
| Packaging     | `pip` + `requirements.txt`                     |

## Goal

Educational desktop software that **visualizes sorting and searching
algorithms step-by-step** with animated bars, live pseudo-code
highlighting, and real-time performance counters.  
A separate **benchmarking module** stress-tests the same algorithms on
large datasets (N = 1 000 000) and reports wall-clock timings.

## Core Features

| #  | Feature                         | Description |
|----|---------------------------------|-------------|
| 1  | Step-by-step animation          | Swaps, comparisons, partitioning rendered frame-by-frame on a bar chart. |
| 2  | Live pseudo-code highlighting   | A pseudo-code panel highlights the line corresponding to the current algorithmic step. |
| 3  | Performance counters            | Comparison count and swap count updated in real time. |
| 4  | Configurable array size (N)     | Slider from 5 to 200 elements. |
| 5  | Animation speed slider          | Adjustable delay from 1ms to 500ms per step. |
| 6  | Input type selection            | Random / Already Sorted / Reversed arrays. |
| 7  | Progress bar                    | Visual progress indicator for step position. |
| 8  | Chip selector UI                | Modern chip-based input type selection. |
| 9  | Pivot strategies                | QuickSort supports first/last/middle/median3 pivot selection. |
| 10 | Custom array input              | User can enter comma-separated values or click bars to edit. |
| 11 | Completed sweep animation       | Green left-to-right sweep after sorting completes. |
| 12 | Color legend                    | Per-algorithm color legend in the control bar. |
| 13 | Complexity badge                | Average/best/worst time complexity displayed. |
| 14 | Natural language explanations   | Enriched step descriptions with comparison outcomes. |

## Architecture

```
├── main.py              ← Entry point (Eel)
├── eel_api.py           ← @eel.expose bridge functions
├── web/
│   ├── index.html       ← Single-page layout
│   ├── css/style.css    ← Dark theme (VisuAlgo-inspired)
│   └── js/
│       ├── bridge.js    ← Main controller + event wiring
│       ├── renderer.js  ← HTML5 Canvas bar renderer
│       ├── state.js     ← Step cache & playback state
│       ├── pseudocode.js
│       ├── stats.js     ← Stats + legend + complexity badge
│       ├── benchmark.js
│       └── modules/
│           ├── algorithms.js
│           └── ds/ds_placeholder.js
└── src/                 ← Python core
    ├── core/
    │   ├── step.py          ← Step dataclass
    │   ├── algorithms.py    ← Generator-based algorithms
    │   └── pseudocode.py    ← Pseudo-code line mappings
    ├── benchmarking/
    │   ├── benchmark_runner.py
    │   └── data_generator.py
    └── utils/
        └── helpers.py
```

## Design Pattern

Algorithms are implemented as **Python generators** that `yield Step`
objects. The Eel bridge (`eel_api.py`) collects all steps into a JSON
list and sends them to the JS frontend in one batch. The `StateManager`
caches all steps client-side, enabling forward/backward navigation
without additional Python calls.
