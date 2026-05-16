/**
 * ds_renderer.js — Canvas renderer cho cấu trúc dữ liệu.
 *
 * Hỗ trợ 4 chế độ vẽ:
 * - Stack: các khối xếp chồng theo chiều dọc (bottom → top)
 * - Queue: các khối nằm ngang (left → right)
 * - LinkedList: các ô nối nhau bằng mũi tên
 * - BST: cây nhị phân với nút và cạnh
 */

class DSRenderer {
  /**
   * @param {string} canvasId — DOM id of the <canvas> element.
   */
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext('2d');
    this._lastStep = null;
    this._emptyType = null;

    this._resizeObserver = new ResizeObserver(() => this.resize());
    this._resizeObserver.observe(this.canvas);
    this.resize();
  }

  resize() {
    const rect = this.canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    this.canvas.width = rect.width * dpr;
    this.canvas.height = rect.height * dpr;
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    this._width = rect.width;
    this._height = rect.height;
    if (this._lastStep) this.drawStep(this._lastStep);
    else if (this._emptyType) this._drawEmptyState(this._emptyType);
  }

  /** Read a CSS custom property value. */
  _css(name) {
    return getComputedStyle(document.documentElement)
      .getPropertyValue(name).trim();
  }

  /** Get the current theme-aware colour palette. */
  _colors() {
    return {
      bg: this._css('--bg-canvas') || '#0B1120',
      panel: this._css('--bg-panel') || '#1E293B',
      card: this._css('--bg-card') || '#273548',
      accent: this._css('--accent') || '#8B5CF6',
      cyan: this._css('--accent-cyan') || '#22D3EE',
      text: this._css('--text-primary') || '#F1F5F9',
      textDim: this._css('--text-dim') || '#64748B',
      border: this._css('--border-strong') || 'rgba(255,255,255,0.14)',
      green: this._css('--bar-found') || '#34D399',
      red: this._css('--bar-swap') || '#EF4444',
      yellow: this._css('--bar-compare') || '#FBBF24',
      blue: this._css('--bar-default') || '#22D3EE',
      purple: this._css('--bar-set') || '#A78BFA',
    };
  }

  /**
   * Main draw dispatcher — reads step.extra.ds_type and routes.
   * @param {Object} step — step dict from Python with extra field.
   */
  drawStep(step) {
    this._lastStep = step;
    this._emptyType = null;
    const dsType = step.extra?.ds_type;
    if (dsType === 'stack') this._drawStack(step);
    else if (dsType === 'queue') this._drawQueue(step);
    else if (dsType === 'linkedlist') this._drawLinkedList(step);
    else if (dsType === 'bst') this._drawBST(step);
    else this._drawGeneric(step);
  }

  /** Clear canvas with theme background. */
  _clear() {
    const c = this._colors();
    this.ctx.fillStyle = c.bg;
    this.ctx.fillRect(0, 0, this._width, this._height);
  }

  /** Get highlight colour for a step type. */
  _highlightColor(type) {
    const c = this._colors();
    const map = {
      push: c.green, pop: c.red, enqueue: c.green, dequeue: c.red,
      insert: c.green, delete: c.red, found: c.green, not_found: c.red,
      compare: c.yellow, highlight: c.cyan, traverse: c.purple,
    };
    return map[type] || c.blue;
  }

  // ── Stack: vertical blocks ──────────────────────────────────────

  _drawStack(step) {
    this._clear();
    const ctx = this.ctx;
    const c = this._colors();
    const arr = step.array_state;
    const n = arr.length;

    const boxW = Math.min(160, this._width * 0.35);
    const boxH = Math.min(40, (this._height - 80) / Math.max(n, 1) - 4);
    const cx = this._width / 2;
    const baseY = this._height - 40;

    // Label
    ctx.fillStyle = c.textDim;
    ctx.font = '12px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('TOP ↑', cx, 20);

    for (let i = 0; i < n; i++) {
      const x = cx - boxW / 2;
      const y = baseY - (i + 1) * (boxH + 4);
      const isHighlighted = step.indices.includes(i) || step.type === 'not_found';
      const isTop = i === n - 1;

      ctx.fillStyle = isHighlighted ? this._highlightColor(step.type)
        : isTop ? c.cyan : c.card;
      ctx.strokeStyle = c.border;
      ctx.lineWidth = 1;

      this._roundRect(x, y, boxW, boxH, 6);
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = c.text;
      ctx.font = `600 ${Math.min(14, boxH * 0.5)}px 'JetBrains Mono', monospace`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(arr[i], cx, y + boxH / 2);
    }

    if (n === 0) {
      ctx.fillStyle = c.textDim;
      ctx.font = '14px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('Stack rỗng', cx, this._height / 2);
    }
  }

  // ── Queue: horizontal blocks ────────────────────────────────────

  _drawQueue(step) {
    this._clear();
    const ctx = this.ctx;
    const c = this._colors();
    const arr = step.array_state;
    const n = arr.length;

    const boxW = Math.max(36, Math.min(80, (this._width - 80) / Math.max(n, 1) - 8));
    const boxH = 50;
    const cy = this._height / 2;
    const totalW = n * boxW + Math.max(0, n - 1) * 8;
    const startX = Math.max(40, (this._width - totalW) / 2);

    // Labels
    ctx.fillStyle = c.textDim;
    ctx.font = '11px Inter, sans-serif';
    ctx.textAlign = 'center';
    if (n > 0) {
      const labelY = cy - boxH / 2 - 10;
      if (n === 1) {
        ctx.fillText('FRONT / REAR', startX + boxW / 2, labelY);
      } else {
        ctx.fillText('FRONT', startX + boxW / 2, labelY);
        ctx.fillText('REAR', startX + (n - 1) * (boxW + 8) + boxW / 2, labelY);
      }
    }

    for (let i = 0; i < n; i++) {
      const x = startX + i * (boxW + 8);
      const y = cy - boxH / 2;
      const isHighlighted = step.indices.includes(i) || step.type === 'not_found';

      ctx.fillStyle = isHighlighted ? this._highlightColor(step.type)
        : i === 0 ? c.cyan : c.card;
      ctx.strokeStyle = c.border;
      ctx.lineWidth = 1;

      this._roundRect(x, y, boxW, boxH, 6);
      ctx.fill();
      ctx.stroke();

      // Arrow to next
      if (i < n - 1) {
        ctx.strokeStyle = c.textDim;
        ctx.lineWidth = 1.5;
        const ax = x + boxW + 1;
        const ay = cy;
        ctx.beginPath();
        ctx.moveTo(ax, ay);
        ctx.lineTo(ax + 6, ay);
        ctx.moveTo(ax + 3, ay - 3);
        ctx.lineTo(ax + 6, ay);
        ctx.lineTo(ax + 3, ay + 3);
        ctx.stroke();
      }

      ctx.fillStyle = c.text;
      ctx.font = `600 14px 'JetBrains Mono', monospace`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(arr[i], x + boxW / 2, cy);
    }

    if (n === 0) {
      ctx.fillStyle = c.textDim;
      ctx.font = '14px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('Hàng đợi rỗng', this._width / 2, cy);
    }
  }

  // ── Linked List: nodes with arrows ──────────────────────────────

  _drawLinkedList(step) {
    this._clear();
    const ctx = this.ctx;
    const c = this._colors();
    const arr = step.array_state;
    const n = arr.length;

    const nodeR = 22;
    const gap = 50;
    const totalW = n * (nodeR * 2) + (n - 1) * gap;
    const startX = Math.max(30, (this._width - totalW) / 2) + nodeR;
    const cy = this._height / 2;

    // HEAD label
    if (n > 0) {
      ctx.fillStyle = c.textDim;
      ctx.font = '11px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('HEAD', startX, cy - nodeR - 12);
    }

    for (let i = 0; i < n; i++) {
      const cx_i = startX + i * (nodeR * 2 + gap);
      const isHighlighted = step.indices.includes(i) || step.type === 'not_found';

      // Arrow to next
      if (i < n - 1) {
        ctx.strokeStyle = c.textDim;
        ctx.lineWidth = 1.5;
        const ax1 = cx_i + nodeR + 2;
        const ax2 = cx_i + nodeR * 2 + gap - nodeR - 2;
        ctx.beginPath();
        ctx.moveTo(ax1, cy);
        ctx.lineTo(ax2, cy);
        // arrowhead
        ctx.moveTo(ax2 - 5, cy - 4);
        ctx.lineTo(ax2, cy);
        ctx.lineTo(ax2 - 5, cy + 4);
        ctx.stroke();
      } else {
        // NULL marker
        ctx.fillStyle = c.textDim;
        ctx.font = '10px JetBrains Mono, monospace';
        ctx.textAlign = 'left';
        ctx.fillText('NULL', cx_i + nodeR + 8, cy + 4);
      }

      // Node circle
      ctx.beginPath();
      ctx.arc(cx_i, cy, nodeR, 0, Math.PI * 2);
      ctx.fillStyle = isHighlighted ? this._highlightColor(step.type) : c.card;
      ctx.fill();
      ctx.strokeStyle = isHighlighted ? this._highlightColor(step.type) : c.border;
      ctx.lineWidth = 2;
      ctx.stroke();

      // Value
      ctx.fillStyle = c.text;
      ctx.font = `600 13px 'JetBrains Mono', monospace`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(arr[i], cx_i, cy);
    }

    if (n === 0) {
      ctx.fillStyle = c.textDim;
      ctx.font = '14px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('Danh sách liên kết rỗng', this._width / 2, cy);
    }
  }

  // ── BST: tree with nodes and edges ──────────────────────────────

  _drawBST(step) {
    this._clear();
    const ctx = this.ctx;
    const c = this._colors();
    const tree = step.extra?.tree;

    if (!tree || !tree.nodes || tree.nodes.length === 0) {
      ctx.fillStyle = c.textDim;
      ctx.font = '14px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('Cây BST rỗng', this._width / 2, this._height / 2);
      return;
    }

    const padX = 40;
    const padY = 50;
    const usableW = this._width - 2 * padX;
    const usableH = this._height - 2 * padY;
    const nodeR = 20;

    // Calculate positions
    const positions = {};
    const maxDepth = Math.max(...tree.nodes.map(n => n.y), 0);
    const levelH = maxDepth > 0 ? usableH / maxDepth : 0;

    for (const node of tree.nodes) {
      positions[node.id] = {
        x: padX + node.x * usableW,
        y: padY + node.y * levelH,
        val: node.val,
        highlight: node.highlight,
      };
    }

    // Draw edges
    ctx.strokeStyle = c.textDim;
    ctx.lineWidth = 1.5;
    for (const edge of tree.edges) {
      const from = positions[edge.from];
      const to = positions[edge.to];
      if (from && to) {
        ctx.beginPath();
        ctx.moveTo(from.x, from.y + nodeR);
        ctx.lineTo(to.x, to.y - nodeR);
        ctx.stroke();
      }
    }

    // Draw nodes
    for (const node of tree.nodes) {
      const p = positions[node.id];
      const hl = step.type === 'not_found' ? 'not_found' : node.highlight;

      ctx.beginPath();
      ctx.arc(p.x, p.y, nodeR, 0, Math.PI * 2);
      ctx.fillStyle = hl ? this._highlightColor(hl) : c.card;
      ctx.fill();
      ctx.strokeStyle = hl ? this._highlightColor(hl) : c.border;
      ctx.lineWidth = 2;
      ctx.stroke();

      ctx.fillStyle = c.text;
      ctx.font = `600 12px 'JetBrains Mono', monospace`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(p.val, p.x, p.y);
    }
  }

  // ── Generic fallback ────────────────────────────────────────────

  _drawGeneric(step) {
    this._clear();
    const ctx = this.ctx;
    const c = this._colors();
    ctx.fillStyle = c.textDim;
    ctx.font = '14px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(step.description || 'No data', this._width / 2, this._height / 2);
  }

  // ── Utility ─────────────────────────────────────────────────────

  _drawEmptyState(dsType) {
    this._clear();
    const ctx = this.ctx;
    const c = this._colors();
    const labelMap = {
      stack: 'Stack is empty',
      queue: 'Queue is empty',
      linkedlist: 'Linked list is empty',
      bst: 'Binary search tree is empty',
    };
    const hintMap = {
      stack: 'Enter a value and choose Push',
      queue: 'Enter a value and choose Enqueue',
      linkedlist: 'Insert a head or tail node to begin',
      bst: 'Insert a root value to begin',
    };

    const cx = this._width / 2;
    const cy = this._height / 2;
    const r = Math.min(68, Math.max(42, this._width * 0.08));

    ctx.save();
    ctx.strokeStyle = c.border;
    ctx.lineWidth = 1.5;
    ctx.setLineDash([5, 5]);
    this._roundRect(cx - r, cy - r - 22, r * 2, r * 1.35, 10);
    ctx.stroke();
    ctx.setLineDash([]);

    ctx.fillStyle = c.card;
    this._roundRect(cx - r + 10, cy - 22, r * 2 - 20, 22, 6);
    ctx.fill();
    ctx.strokeStyle = c.border;
    ctx.stroke();

    ctx.fillStyle = c.text;
    ctx.font = '600 15px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(labelMap[dsType] || 'No data yet', cx, cy + r * 0.75);

    ctx.fillStyle = c.textDim;
    ctx.font = '12px Inter, sans-serif';
    ctx.fillText(hintMap[dsType] || 'Choose an operation to begin', cx, cy + r * 0.75 + 22);
    ctx.restore();
  }

  _roundRect(x, y, w, h, r) {
    const ctx = this.ctx;
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + w - r, y);
    ctx.quadraticCurveTo(x + w, y, x + w, y + r);
    ctx.lineTo(x + w, y + h - r);
    ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    ctx.lineTo(x + r, y + h);
    ctx.quadraticCurveTo(x, y + h, x, y + h - r);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.closePath();
  }

  clear(dsType = null) {
    this._lastStep = null;
    this._emptyType = dsType;
    if (dsType) this._drawEmptyState(dsType);
    else this._clear();
  }
}
