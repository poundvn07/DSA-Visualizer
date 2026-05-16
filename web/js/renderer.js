/**
 * renderer.js — HTML5 Canvas drawing engine for array visualisation.
 *
 * Renders vertical bars proportional to element values. Supports
 * colour-coded highlighting and optional value labels when N ≤ 30.
 *
 * Theme-aware: reads bar colours from CSS custom properties via
 * getComputedStyle so they automatically respond to Dark/Light toggle.
 */

class Renderer {
  /**
   * @param {string} canvasId — DOM id of the <canvas> element.
   */
  constructor(canvasId) {
    /** @type {HTMLCanvasElement} */
    this.canvas = document.getElementById(canvasId);
    /** @type {CanvasRenderingContext2D} */
    this.ctx = this.canvas.getContext('2d');
    this._lastArray = [];
    this._lastHighlights = {};

    // Match canvas pixel size to its CSS layout size.
    this._resizeObserver = new ResizeObserver(() => this.resize());
    this._resizeObserver.observe(this.canvas);
    this.resize();
  }

  /**
   * Read the current bar colours from CSS custom properties.
   * This ensures colours update automatically when the theme changes.
   * @returns {Object<string, string>}
   */
  _getBarColours() {
    const s = getComputedStyle(document.documentElement);
    return {
      default: s.getPropertyValue('--bar-default').trim() || '#22D3EE',
      compare: s.getPropertyValue('--bar-compare').trim() || '#FBBF24',
      swap: s.getPropertyValue('--bar-swap').trim() || '#EF4444',
      pivot: s.getPropertyValue('--bar-pivot').trim() || '#F97316',
      found: s.getPropertyValue('--bar-found').trim() || '#34D399',
      set: s.getPropertyValue('--bar-set').trim() || '#A78BFA',
      range: s.getPropertyValue('--bar-range').trim() || '#38BDF8',
      not_found: s.getPropertyValue('--bar-swap').trim() || '#EF4444',
      excluded: s.getPropertyValue('--bar-excluded').trim() || '#1E293B',
      done: s.getPropertyValue('--bar-done').trim() || '#34D399',
      hover: s.getPropertyValue('--bar-hover').trim() || '#60A5FA',
    };
  }

  /**
   * Resize the canvas internal resolution to match its CSS size
   * and redraw the last array state.
   */
  resize() {
    const rect = this.canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    this.canvas.width = rect.width * dpr;
    this.canvas.height = rect.height * dpr;
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    this._width = rect.width;
    this._height = rect.height;

    if (this._lastArray.length > 0) {
      this.drawArray(this._lastArray, this._lastHighlights);
    }
  }

  /**
   * Compute the bar layout metrics for the current array.
   * @param {number} n — number of elements.
   * @returns {{ padX: number, padY: number, gap: number, barW: number }}
   */
  _barMetrics(n) {
    const w = this._width;
    const padX = 8;
    const padY = 24;
    const gap = Math.max(1, Math.min(3, (w - 2 * padX) / n * 0.12));
    const barW = Math.max(1, (w - 2 * padX - (n - 1) * gap) / n);
    return { padX, padY, gap, barW };
  }

  /**
   * Given a client-X coordinate, return the bar index it falls on,
   * or -1 if outside all bars.
   * @param {number} clientX
   * @returns {number}
   */
  hitTestBar(clientX) {
    const n = this._lastArray.length;
    if (n === 0) return -1;
    const rect = this.canvas.getBoundingClientRect();
    const x = clientX - rect.left;
    const { padX, gap, barW } = this._barMetrics(n);
    const idx = Math.floor((x - padX) / (barW + gap));
    if (idx < 0 || idx >= n) return -1;
    return idx;
  }

  /**
   * Draw the array as vertical bars with rounded tops.
   *
   * @param {number[]} arrayState — the current array values.
   * @param {Object<number, string>} highlights — index → type override.
   */
  drawArray(arrayState, highlights = {}) {
    this._lastArray = arrayState;
    this._lastHighlights = highlights;

    const ctx = this.ctx;
    const w = this._width;
    const h = this._height;
    const colours = this._getBarColours();

    // Clear with canvas background colour.
    const bgCanvas = getComputedStyle(document.documentElement)
      .getPropertyValue('--bg-canvas').trim() || '#0B1120';
    ctx.fillStyle = bgCanvas;
    ctx.fillRect(0, 0, w, h);

    const n = arrayState.length;
    if (n === 0) return;

    const { padX, padY, gap, barW } = this._barMetrics(n);
    const maxVal = Math.max(...arrayState, 1);
    const usableH = h - 2 * padY;

    for (let i = 0; i < n; i++) {
      const barH = Math.max(2, (arrayState[i] / maxVal) * usableH);
      const x = padX + i * (barW + gap);
      const y = h - padY - barH;

      const type = highlights[i] || 'default';
      ctx.fillStyle = colours[type] || colours.default;

      // Draw bar with rounded top corners when wide enough.
      if (barW >= 6) {
        const r = Math.min(4, barW / 2);
        ctx.beginPath();
        ctx.moveTo(x, y + barH);
        ctx.lineTo(x, y + r);
        ctx.quadraticCurveTo(x, y, x + r, y);
        ctx.lineTo(x + barW - r, y);
        ctx.quadraticCurveTo(x + barW, y, x + barW, y + r);
        ctx.lineTo(x + barW, y + barH);
        ctx.closePath();
        ctx.fill();
      } else {
        ctx.fillRect(x, y, barW, barH);
      }

      // Value labels when N ≤ 30.
      if (n <= 30 && barW >= 14) {
        const textColor = getComputedStyle(document.documentElement)
          .getPropertyValue('--text-primary').trim() || '#F1F5F9';
        ctx.fillStyle = textColor;
        ctx.font = `500 ${Math.min(11, barW * 0.65)}px 'JetBrains Mono', monospace`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'bottom';
        ctx.fillText(arrayState[i], x + barW / 2, y - 3);
      }
    }
  }

  /**
   * Parse a Step object and render it with appropriate highlights.
   * Also updates the natural-language explanation element.
   *
   * If the step carries subarray metadata (QuickSort / MergeSort),
   * renders the recursive split view instead of the flat bar chart.
   *
   * @param {Object} step — a step dict from Python.
   */
  animateStep(step) {
    // Recursive subarray view for divide-and-conquer algorithms.
    if (step.extra && step.extra.subarray) {
      this._drawRecursiveStep(step);
      const nlEl = document.getElementById('nl-explanation');
      if (nlEl) {
        nlEl.textContent = step.description || '';
        if (step.type === 'swap' || step.type === 'found') {
          const colours = this._getBarColours();
          nlEl.style.color = step.type === 'found' ? colours.found : colours.swap;
          setTimeout(() => { nlEl.style.color = ''; }, 600);
        } else {
          nlEl.style.color = '';
        }
      }
      return;
    }

    // Standard flat bar-chart view.
    const highlights = {};

    if (step.type === 'range' && step.indices.length === 3) {
      // Binary search: highlight [low..high] range, special mid.
      const [low, mid, high] = step.indices;
      for (let i = 0; i < step.array_state.length; i++) {
        if (i < low || i > high) {
          highlights[i] = 'excluded';
        } else if (i === mid) {
          highlights[i] = 'compare';
        } else {
          highlights[i] = 'range';
        }
      }
    } else {
      for (const idx of step.indices) {
        highlights[idx] = step.type;
      }
    }

    this.drawArray(step.array_state, highlights);

    // Natural language explanation line.
    const nlEl = document.getElementById('nl-explanation');
    if (nlEl) {
      nlEl.textContent = step.description || '';
      if (step.type === 'swap' || step.type === 'found') {
        const colours = this._getBarColours();
        nlEl.style.color = step.type === 'found' ? colours.found : colours.swap;
        setTimeout(() => { nlEl.style.color = ''; }, 600);
      } else {
        nlEl.style.color = '';
      }
    }
  }

  /**
   * Draw a recursive step in a single canvas (VisuAlgo style).
   *
   * All bars live on one chart. Bars inside the active subarray
   * [left..right] are shifted DOWN by `depth * depthOffset` pixels,
   * creating a visual "step-down" during recursion. Bars outside the
   * active range stay at the top baseline and are dimmed.
   *
   * @param {Object} step — step dict with extra.subarray.
   * @private
   */
  _drawRecursiveStep(step) {
    const ctx = this.ctx;
    const w = this._width;
    const h = this._height;
    const colours = this._getBarColours();
    const { left, right, depth } = step.extra.subarray;
    const arr = step.array_state;
    const n = arr.length;

    // Clear canvas.
    const bgCanvas = getComputedStyle(document.documentElement)
      .getPropertyValue('--bg-canvas').trim() || '#0B1120';
    ctx.fillStyle = bgCanvas;
    ctx.fillRect(0, 0, w, h);

    if (n === 0) return;

    // Layout constants.
    const padX = 8;
    const padYTop = 20;           // top margin for value labels
    const padYBot = 12;           // bottom margin
    const depthOffset = 30;       // pixels each depth level shifts down
    const maxDepthShift = 5;      // cap visual depth
    const clampedDepth = Math.min(depth, maxDepthShift);

    // Bar metrics (shared for all bars — single array).
    const gap = Math.max(1, Math.min(3, (w - 2 * padX) / n * 0.12));
    const barW = Math.max(1, (w - 2 * padX - (n - 1) * gap) / n);

    // The usable height is reduced to leave room for depth shifting.
    const totalDepthRoom = maxDepthShift * depthOffset;
    const usableH = h - padYTop - padYBot - totalDepthRoom;
    const maxVal = Math.max(...arr, 1);

    // Baseline Y for depth=0 bars (anchored from the top).
    const baselineY = padYTop + usableH;

    for (let i = 0; i < n; i++) {
      const inRange = i >= left && i <= right;
      const shift = inRange ? clampedDepth * depthOffset : 0;

      const barH = Math.max(2, (arr[i] / maxVal) * usableH);
      const x = padX + i * (barW + gap);
      const y = baselineY - barH + shift;

      // Determine colour and opacity.
      if (!inRange) {
        ctx.globalAlpha = 0.18;
        ctx.fillStyle = colours.default;
      } else {
        ctx.globalAlpha = 1.0;
        if (step.indices.includes(i)) {
          ctx.fillStyle = colours[step.type] || colours.default;
        } else {
          ctx.fillStyle = colours.default;
        }
      }

      // Draw bar with rounded top when wide enough.
      if (barW >= 6) {
        const r = Math.min(4, barW / 2);
        ctx.beginPath();
        ctx.moveTo(x, y + barH);
        ctx.lineTo(x, y + r);
        ctx.quadraticCurveTo(x, y, x + r, y);
        ctx.lineTo(x + barW - r, y);
        ctx.quadraticCurveTo(x + barW, y, x + barW, y + r);
        ctx.lineTo(x + barW, y + barH);
        ctx.closePath();
        ctx.fill();
      } else {
        ctx.fillRect(x, y, barW, barH);
      }

      // Value label above bar (only for in-range bars when N ≤ 30).
      if (n <= 30 && barW >= 14 && inRange) {
        ctx.globalAlpha = 1.0;
        const textColor = getComputedStyle(document.documentElement)
          .getPropertyValue('--text-primary').trim() || '#F1F5F9';
        ctx.fillStyle = textColor;
        ctx.font = `600 ${Math.min(11, barW * 0.6)}px 'JetBrains Mono', monospace`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'bottom';
        ctx.fillText(arr[i], x + barW / 2, y - 2);
      }
      ctx.globalAlpha = 1.0;
    }

    // Draw a subtle depth indicator line under the active subarray.
    if (left <= right && clampedDepth > 0) {
      const shift = clampedDepth * depthOffset;
      const lineY = baselineY + shift + 4;
      const lineL = padX + left * (barW + gap);
      const lineR = padX + right * (barW + gap) + barW;

      const textDim = getComputedStyle(document.documentElement)
        .getPropertyValue('--text-dim').trim() || '#64748B';

      ctx.strokeStyle = textDim;
      ctx.globalAlpha = 0.5;
      ctx.lineWidth = 1;
      ctx.setLineDash([3, 3]);
      ctx.beginPath();
      ctx.moveTo(lineL, lineY);
      ctx.lineTo(lineR, lineY);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.globalAlpha = 1.0;

      // Depth label.
      ctx.fillStyle = textDim;
      ctx.font = '9px Inter, sans-serif';
      ctx.textAlign = 'right';
      ctx.fillText(`depth ${depth}`, lineR, lineY + 11);
    }

    // Cache for redraw on resize.
    this._lastArray = arr;
    this._lastHighlights = {};
    for (const idx of step.indices) this._lastHighlights[idx] = step.type;
  }

  /**
   * Completed sweep animation.
   * After the final step, animate a left-to-right sweep colouring
   * each bar green one by one with a 30ms delay between bars.
   *
   * @param {number[]} arrayState — the final sorted array.
   */
  completedSweep(arrayState, type = 'done') {
    const sweep = (i) => {
      if (i >= arrayState.length) return;
      const highlights = {};
      for (let k = 0; k <= i; k++) highlights[k] = type;
      this.drawArray(arrayState, highlights);
      setTimeout(() => sweep(i + 1), 30);
    };
    sweep(0);
  }

  /** Clear the canvas to an empty state. */
  clear() {
    this._lastArray = [];
    this._lastHighlights = {};
    const bgCanvas = getComputedStyle(document.documentElement)
      .getPropertyValue('--bg-canvas').trim() || '#0B1120';
    this.ctx.fillStyle = bgCanvas;
    this.ctx.fillRect(0, 0, this._width, this._height);
  }
}
