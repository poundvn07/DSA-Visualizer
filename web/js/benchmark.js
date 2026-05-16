/**
 * benchmark.js — Live Inline Benchmark Suite & Charting Logic.
 *
 * Integrates directly into the home interface dashboard, streaming logs
 * line-by-line and dynamically animating visual comparisons upon finish.
 */

(function () {
  const output = document.getElementById('inline-benchmark-output');
  const btnRun = document.getElementById('btn-inline-run-benchmark');
  const btnCancel = document.getElementById('btn-inline-cancel-benchmark');
  const statusSpan = document.getElementById('inline-benchmark-status');
  const progressFill = document.getElementById('inline-benchmark-progress-fill');
  const chartsContainer = document.getElementById('inline-charts-container');
  const chartsBarsContainer = document.getElementById('inline-charts-bars');
  const btnSidebarBench = document.getElementById('btn-benchmark');

  let currentAlgo = '';
  let resultsData = {};
  let completedRuns = 0;
  let cancelRequested = false;
  const TOTAL_RUNS = 30;

  if (btnSidebarBench) {
    btnSidebarBench.addEventListener('click', () => {
      const sec = document.querySelector('#section-benchmark');
      if (sec) sec.scrollIntoView({ behavior: 'smooth' });
    });
  }

  /** Render the visual execution time comparison bar charts. */
  function renderCharts() {
    if (!chartsContainer || !chartsBarsContainer) return;

    chartsContainer.classList.remove('hidden');
    chartsBarsContainer.innerHTML = '';

    const algos = [
      { key: 'quicksort', name: 'QuickSort', val: resultsData.quicksort || 0 },
      { key: 'heapsort', name: 'HeapSort', val: resultsData.heapsort || 0 },
      { key: 'mergesort', name: 'MergeSort', val: resultsData.mergesort || 0 },
    ];

    const maxVal = Math.max(...algos.map((a) => a.val), 1);

    algos.forEach((algo) => {
      const barWrap = document.createElement('div');
      barWrap.className = 'bench-bar-container';

      const labelRow = document.createElement('div');
      labelRow.className = 'bench-bar-label';
      labelRow.innerHTML = `<span>${algo.name}</span><span style="font-family:'JetBrains Mono', monospace; color:var(--text-secondary);">${
        algo.val ? algo.val.toFixed(2) + ' ms' : 'N/A'
      }</span>`;

      const track = document.createElement('div');
      track.className = 'bench-bar-track';

      const fill = document.createElement('div');
      fill.className = `bench-bar-fill ${algo.key}`;
      fill.style.width = '0%';

      track.appendChild(fill);
      barWrap.appendChild(labelRow);
      barWrap.appendChild(track);
      chartsBarsContainer.appendChild(barWrap);

      // Smooth trigger for visual expansion animation
      requestAnimationFrame(() => {
        setTimeout(() => {
          const pct = algo.val ? Math.max(8, (algo.val / maxVal) * 100) : 0;
          fill.style.width = pct + '%';
        }, 150);
      });
    });
  }

  /** Start live execution via Python eel. */
  function runInlineBenchmark() {
    if (!output || !btnRun) return;

    output.textContent = 'Initializing array of 1,000,000 random integers...\nStarting live performance benchmarking suite...\n';
    btnRun.disabled = true;
    if (btnCancel) {
      btnCancel.disabled = false;
      btnCancel.classList.remove('hidden');
    }
    btnRun.innerHTML = `<svg class="icon-line" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" stroke-dasharray="32" stroke-dashoffset="0"><animate attributeName="stroke-dashoffset" values="0;32" dur="1s" repeatCount="indefinite"/></circle></svg><span>Running Suite...</span>`;
    if (statusSpan) statusSpan.textContent = 'Executing 10 iterations per algorithm...';
    if (progressFill) progressFill.style.width = '0%';

    if (chartsContainer) chartsContainer.classList.add('hidden');

    currentAlgo = '';
    resultsData = {};
    completedRuns = 0;
    cancelRequested = false;

    eel.run_benchmark()();

    // Safety fallback release
    setTimeout(() => {
      btnRun.disabled = false;
      if (btnCancel) btnCancel.classList.add('hidden');
      btnRun.innerHTML = `<svg class="icon-line" viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg><span>Start Live Benchmark</span>`;
      if (statusSpan && statusSpan.textContent.includes('Executing')) {
        statusSpan.textContent = 'Suite completed or timed out';
      }
    }, 150_000);
  }

  if (btnRun) {
    btnRun.addEventListener('click', runInlineBenchmark);
  }

  if (btnCancel) {
    btnCancel.addEventListener('click', () => {
      cancelRequested = true;
      btnCancel.disabled = true;
      if (statusSpan) statusSpan.textContent = 'Cancelling after current run...';
      if (typeof eel.cancel_benchmark === 'function') eel.cancel_benchmark()();
    });
  }

  /**
   * Stream output listener invoked by eel.on_benchmark_line.
   */
  eel.expose(on_benchmark_line);
  function on_benchmark_line(line) {
    if (!output) return;

    output.textContent += line + '\n';
    output.scrollTop = output.scrollHeight;

    const lower = line.toLowerCase();
    if (lower.includes('running quicksort')) currentAlgo = 'quicksort';
    else if (lower.includes('running heapsort')) currentAlgo = 'heapsort';
    else if (lower.includes('running mergesort')) currentAlgo = 'mergesort';

    const runMatch = line.match(/\[(\d+)\/10\]/);
    if (runMatch) {
      completedRuns = Math.min(TOTAL_RUNS, completedRuns + 1);
      if (progressFill) progressFill.style.width = `${(completedRuns / TOTAL_RUNS) * 100}%`;
      if (statusSpan && !cancelRequested) {
        statusSpan.textContent = `Completed ${completedRuns} / ${TOTAL_RUNS} timed runs`;
      }
    }

    if (lower.includes('average')) {
      const match = line.match(/Average\s*:\s*([\d.]+)\s*ms/i);
      if (match && currentAlgo) {
        resultsData[currentAlgo] = parseFloat(match[1]);
      }
    }

    if (lower.includes('benchmark cancelled')) {
      btnRun.disabled = false;
      if (btnCancel) btnCancel.classList.add('hidden');
      btnRun.innerHTML = `<svg class="icon-line" viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg><span>Start Live Benchmark</span>`;
      if (statusSpan) statusSpan.textContent = `Cancelled at ${completedRuns} / ${TOTAL_RUNS} timed runs`;
    }

    if (lower.includes('benchmark complete')) {
      btnRun.disabled = false;
      if (btnCancel) btnCancel.classList.add('hidden');
      btnRun.innerHTML = `<svg class="icon-line" viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg><span>Start Live Benchmark</span>`;
      if (statusSpan) statusSpan.textContent = 'Suite completed successfully';
      if (progressFill) progressFill.style.width = '100%';
      renderCharts();
    }
  }
})();
