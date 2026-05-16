/**
 * stats.js — Live statistics panel, color legend, and complexity badge.
 *
 * Updates the algorithm name, N, comparisons, swaps, and current step
 * count on every animation frame.
 *
 * Legend colours now read from CSS custom properties for theme awareness.
 */

// ── Color Legend Map (using CSS variable names) ──────────────────────

const LEGEND_MAP = {
  quicksort:    [['Default','--bar-default'],['Pivot','--bar-pivot'],
                 ['Compare','--bar-compare'],['Swap','--bar-swap']],
  heapsort:     [['Default','--bar-default'],['Root','--bar-pivot'],
                 ['Compare','--bar-compare'],['Swap','--bar-swap']],
  mergesort:    [['Default','--bar-default'],['Left','--bar-set'],
                 ['Right','--bar-range'],['Placing','--bar-compare']],
  binarysearch: [['Default','--bar-default'],['Range','--bar-set'],
                 ['Mid','--bar-compare'],['Excluded','--bar-excluded'],
                 ['Found','--bar-found']],
};

/**
 * Render the color legend for the given algorithm into the control bar.
 * Reads actual colours from CSS custom properties so they match the theme.
 * @param {string} algorithm — lower-case algorithm key.
 */
function renderLegend(algorithm) {
  const wrap = document.getElementById('color-legend');
  if (!wrap) return;
  const items = LEGEND_MAP[algorithm] ?? [];
  const s = getComputedStyle(document.documentElement);
  wrap.innerHTML = items.map(([label, varName]) => {
    const color = s.getPropertyValue(varName).trim();
    return `<span class="legend-item">
       <span class="legend-swatch" style="background:${color}"></span>
       ${label}
     </span>`;
  }).join('');
}


// ── Complexity Map ───────────────────────────────────────────────────

const COMPLEXITY = {
  quicksort:    { avg: 'O(n log n)', worst: 'O(n²)',     best: 'O(n log n)', space: 'O(log n)' },
  heapsort:     { avg: 'O(n log n)', worst: 'O(n log n)', best: 'O(n log n)', space: 'O(1)' },
  mergesort:    { avg: 'O(n log n)', worst: 'O(n log n)', best: 'O(n log n)', space: 'O(n)' },
  binarysearch: { avg: 'O(log n)',   worst: 'O(log n)',   best: 'O(1)',       space: 'O(1)' },
};

/**
 * Update the complexity badge in the stats panel.
 * @param {string} algorithm — lower-case algorithm key.
 */
function updateComplexityBadge(algorithm) {
  const c = COMPLEXITY[algorithm];
  const el = document.getElementById('complexity-badge');
  if (!el) return;
  if (!c) { el.innerHTML = ''; return; }
  
  el.className = 'complexity-table';
  el.innerHTML = `
    <div style="margin-bottom:8px; font-size:11px; color:var(--text-dim);">Time Complexity</div>
    <div class="stat-row"><span class="stat-key">Best</span><span class="stat-val">${c.best}</span></div>
    <div class="stat-row"><span class="stat-key">Average</span><span class="stat-val">${c.avg}</span></div>
    <div class="stat-row"><span class="stat-key">Worst</span><span class="stat-val">${c.worst}</span></div>
    
    <div style="margin-top:16px; margin-bottom:8px; font-size:11px; color:var(--text-dim);">Space Complexity</div>
    <div class="stat-row"><span class="stat-key">Worst</span><span class="stat-val">${c.space}</span></div>
  `;
}


// ── StatsPanel Class ─────────────────────────────────────────────────

class StatsPanel {
  constructor() {
    this._elAlgo  = document.getElementById('stat-algo');
    this._elN     = document.getElementById('stat-n');
    this._elComp  = document.getElementById('stat-comp');
    this._elSwaps = document.getElementById('stat-swaps');
    this._elStep  = document.getElementById('stat-step');
  }

  /**
   * Update all stats from a step object.
   *
   * @param {Object} step — step dict with comparisons, swaps, array_state.
   * @param {number} current — 1-based current step number.
   * @param {number} total — total number of steps.
   */
  update(step, current, total) {
    this._elComp.textContent  = step.comparisons;
    this._elSwaps.textContent = step.swaps;
    this._elN.textContent     = step.array_state.length;
    this._elStep.textContent  = `${current} / ${total}`;
  }

  /**
   * Set the algorithm display name and update legend + complexity badge.
   * @param {string} name — display name (e.g. "QuickSort").
   * @param {string} [algoKey] — lower-case key (e.g. "quicksort").
   */
  setAlgorithm(name, algoKey) {
    this._elAlgo.textContent = name;
    if (algoKey) {
      renderLegend(algoKey);
      updateComplexityBadge(algoKey);
    }
  }

  /**
   * Set the array size.
   * @param {number} n
   */
  setN(n) {
    this._elN.textContent = n;
  }

  /** Reset all stats to defaults. */
  reset() {
    this._elAlgo.textContent  = '—';
    this._elN.textContent     = '—';
    this._elComp.textContent  = '0';
    this._elSwaps.textContent = '0';
    this._elStep.textContent  = '0 / 0';
  }
}
