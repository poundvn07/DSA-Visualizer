# DSA Visualizer — Premium Algorithm & Data Structure Visualizer

A professional, high-performance educational tool designed to **visualize sorting algorithms, searching techniques, and data structures** in real-time. Built with a focus on aesthetics and clarity, it provides step-by-step execution details, live pseudo-code highlighting, and a robust benchmarking suite.

---

## ✨ Features

- **🚀 Premium UI/UX**: Inspired by modern design systems (Linear, Vercel), featuring a sleek dark/light mode interface with glassmorphism and smooth micro-animations.
- **📊 Algorithm Visualization**:
  - **Sorting**: QuickSort (Lomuto), HeapSort, and MergeSort with frame-by-frame swap/comparison rendering.
  - **Searching**: Binary Search with clear success (Green) and failure (Red sweep) visual feedback.
- **🏗️ Data Structures**: Fully interactive visualizations for **Stack, Queue, Singly Linked List, and Binary Search Tree (BST)**.
- **💻 Live Pseudo-code**: Synchronized code highlighting that tracks the algorithm's execution line-by-line.
- **📈 Benchmarking Module**: Test algorithm performance on large datasets (up to 1M elements) with detailed CLI and UI output.
- **🕹️ Interactive Controls**: 
  - **Multi-speed playback**: Adjustable speed from 0.5x to 4.0x.
  - **Step-by-step navigation**: Advance or retreat through the algorithm's history.
  - **Custom Inputs**: Generate random, sorted, or nearly sorted arrays.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+ (Logic Simulation via Generators)
- **Bridge**: [Eel](https://github.com/python-eel/Eel) (Python-to-JS communication)
- **Frontend**: Vanilla JS, CSS3 (Variables + Flexbox), HTML5 Canvas
- **Design**: Modern Dark Theme (Primary: `#8B5CF6` Purple)
- **Typography**: [Inter](https://rsms.me/inter/) for UI, [JetBrains Mono](https://www.jetbrains.com/lp/mono/) for code.

---

## 🚀 Quick Start

### 1. Prerequisites
Ensure you have Python 3.10 or higher installed.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the App
```bash
python main.py
```
*The application will open in your default web browser.*

---

## 📁 Project Structure

```text
├── main.py              ← Application Entry Point
├── eel_api.py           ← Python-JS Bridge (Exposed functions)
├── src/
│   ├── core/            ← Algorithm & Data Structure Logic (Generators)
│   └── benchmarking/    ← Performance Testing Module
├── web/
│   ├── index.html       ← SPA Structure
│   ├── css/             ← Premium Styling (Dark/Light modes)
│   └── js/              ← Visualizer Core (Renderer, State Manager)
├── tests/               ← Unit Tests for Core Logic
└── docs/                ← Project Specifications & Guides
```

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | Play / Pause |
| `→` | Step Forward |
| `←` | Step Backward |
| `N` | Generate New Data |
| `R` | Reset Current View |

---

## ⚖️ License
This project is for educational purposes. Feel free to use, modify, and learn from it.