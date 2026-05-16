/**
 * pseudocode.js — Pseudo-code panel rendering and line highlighting.
 *
 * Loads pseudo-code lines from Python via eel, renders them into the
 * DOM, and highlights the currently executing line with a CSS class.
 */

class PseudocodePanel {
  /**
   * @param {string} containerId — DOM id of the scrollable container.
   */
  constructor(containerId) {
    /** @type {HTMLElement} */
    this.container = document.getElementById(containerId);
    /** @type {HTMLElement[]} */
    this.lineElements = [];
    /** @type {number} Currently highlighted line index. */
    this._activeLine = -1;
  }

  /**
   * Load pseudo-code lines for an algorithm and render them.
   * @param {string[]} lines — array of pseudo-code strings.
   */
  load(lines) {
    this.container.innerHTML = '';
    this.lineElements = [];
    this._activeLine = -1;

    for (let i = 0; i < lines.length; i++) {
      const div = document.createElement('div');
      div.classList.add('pseudo-line');
      div.textContent = lines[i].replace(/(\S)\s{4,}(\/\/)/g, '$1  $2');
      this.container.appendChild(div);
      this.lineElements.push(div);
    }
  }

  /**
   * Highlight a single line and dim all others.
   * @param {number} index — zero-based line index.
   */
  highlightLine(index) {
    if (this._activeLine === index) return;

    // Remove previous highlight.
    if (this._activeLine >= 0 && this._activeLine < this.lineElements.length) {
      this.lineElements[this._activeLine].classList.remove('active');
    }

    // Apply new highlight.
    if (index >= 0 && index < this.lineElements.length) {
      this.lineElements[index].classList.add('active');
      // Scroll the highlighted line into view.
      this.lineElements[index].scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }

    this._activeLine = index;
  }

  /** Remove all highlights. */
  reset() {
    for (const el of this.lineElements) {
      el.classList.remove('active');
    }
    this._activeLine = -1;
  }

  /** Clear the panel entirely. */
  clear() {
    this.container.innerHTML = '';
    this.lineElements = [];
    this._activeLine = -1;
  }
}
