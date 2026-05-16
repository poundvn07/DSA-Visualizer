# DSA Visualizer — Algorithm Visualizer & Benchmarking

An educational desktop application that **visualises sorting and
searching algorithms step-by-step** with animated bars, live
pseudo-code highlighting, real-time performance counters, and a
benchmarking module for large datasets.

Built with **Python + Eel + HTML5 Canvas** — the Python core generates
algorithm steps as JSON, and the web frontend animates them in a
VisuAlgo-inspired dark-theme interface.

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch the application
python main.py
# → Eel will open the app in your default browser

# 3. (Optional) Run benchmarks from CLI
python -m src.benchmarking.benchmark_runner
```

## Features

| Feature | Description |
|---------|-------------|
| **Step-by-step animation** | Swaps, comparisons, partitioning rendered frame-by-frame |
| **Live pseudo-code** | Highlighted line synced with each algorithmic step |
| **Performance counters** | Comparison & swap counts updated in real time |
| **Backward navigation** | Step backward through cached steps |
| **Configurable parameters** | Array size (5–200), speed (1–500ms), input type |
| **Benchmarking** | 10× runs on 1M elements for QuickSort, HeapSort, MergeSort |
| **Data Structures tab** | Placeholder cards for future Stack, Queue, Tree, Graph visualisations |

## Supported Algorithms

| Algorithm | Type | Complexity |
|-----------|------|------------|
| QuickSort (Lomuto) | Sorting | O(n log n) |
| HeapSort | Sorting | O(n log n) |
| MergeSort | Sorting | O(n log n) |
| Binary Search | Searching | O(log n) |

## Architecture

```
├── main.py              ← Entry point (Eel)
├── eel_api.py           ← @eel.expose bridge functions
├── web/
│   ├── index.html       ← Single-page layout
│   ├── css/style.css    ← Dark theme styles
│   └── js/
│       ├── bridge.js    ← Main controller + event wiring
│       ├── renderer.js  ← HTML5 Canvas bar renderer
│       ├── state.js     ← Step cache & playback state
│       ├── pseudocode.js
│       ├── stats.js
│       ├── benchmark.js
│       └── modules/
│           ├── algorithms.js
│           └── ds/ds_placeholder.js
└── src/                 ← Python core (unchanged)
    ├── core/            ← Step dataclass, algorithm generators, pseudocode
    ├── benchmarking/    ← Benchmark runner + data generator
    └── utils/           ← Helpers
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | Play / Pause |
| `→` | Step forward |
| `←` | Step backward |
| `N` | New array |
| `R` | Reset |

## Tech Stack

- **Backend**: Python 3.10+ with [Eel](https://github.com/python-eel/Eel)
- **Frontend**: Vanilla HTML/CSS/JS, HTML5 Canvas API
- **Design**: VisuAlgo-inspired dark theme (Catppuccin Mocha palette)
- **Fonts**: Inter (UI), JetBrains Mono (code/stats)