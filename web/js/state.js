/**
 * state.js — Client-side step cache and playback state manager.
 *
 * Stores the full list of steps received from Python, manages a cursor
 * for forward/backward navigation, drives the play loop via
 * setInterval, updates the progress bar (Feature 1), and triggers
 * a completed sweep animation (Feature 6).
 */

class StateManager {
  constructor() {
    /** @type {Object[]} Full list of step dicts from Python. */
    this.steps = [];
    /** @type {number} Current cursor position (-1 = before first step). */
    this.cursor = -1;
    /** @type {boolean} Whether continuous playback is active. */
    this.playing = false;
    /** @type {number|null} Interval ID for the play loop. */
    this.timer = null;
  }

  /**
   * Update the progress bar and label to reflect current cursor position.
   * Called after every cursor change.
   */
  updateProgress() {
    const total = this.steps.length;
    const pct = total === 0 ? 0 : ((this.cursor + 1) / total) * 100;
    const fillEl = document.getElementById('progress-fill');
    const labelEl = document.getElementById('progress-label');
    if (fillEl) fillEl.style.width = pct + '%';
    if (labelEl) labelEl.textContent =
      `Step ${Math.max(this.cursor + 1, 0)} / ${total}`;
  }

  /**
   * Load a new set of steps and reset the cursor.
   * @param {Object[]} steps — array of step dicts from eel.
   */
  load(steps) {
    this.steps = steps;
    this.cursor = -1;
    this.playing = false;
    if (this.timer !== null) {
      clearInterval(this.timer);
      this.timer = null;
    }
    this.updateProgress();
  }

  /**
   * Advance the cursor by one and return the step, or null if at end.
   * @returns {Object|null}
   */
  stepForward() {
    if (this.cursor + 1 < this.steps.length) {
      this.cursor++;
      this.updateProgress();
      return this.steps[this.cursor];
    }
    return null;
  }

  /**
   * Move the cursor back by one and return the step, or null if at start.
   * @returns {Object|null}
   */
  stepBackward() {
    if (this.cursor > 0) {
      this.cursor--;
      this.updateProgress();
      return this.steps[this.cursor];
    }
    return null;
  }

  /**
   * Start continuous playback using setInterval.
   *
   * When playback reaches the final step, triggers the completed
   * sweep animation on the renderer (Feature 6).
   *
   * @param {Renderer} renderer — canvas renderer instance.
   * @param {StatsPanel} stats — live stats panel instance.
   * @param {PseudocodePanel} pseudocode — pseudo-code panel instance.
   * @param {number} delayMs — milliseconds between frames.
   * @param {function} onStop — callback when playback stops.
   */
  play(renderer, stats, pseudocode, delayMs, onStop) {
    if (this.playing) return;
    this.playing = true;

    this.timer = setInterval(() => {
      const step = this.stepForward();
      if (step === null) {
        this.pause();
        if (onStop) onStop();
        return;
      }
      renderer.animateStep(step);
      pseudocode.highlightLine(step.highlight_line);
      stats.update(step, this.cursor + 1, this.steps.length);

      // Feature 6: completed sweep when reaching the last step.
      if (this.cursor === this.steps.length - 1) {
        this.pause();
        if (onStop) onStop();
        if (renderer.completedSweep) {
          renderer.completedSweep(step.array_state, step);
        }
      }
    }, delayMs);
  }

  /** Pause continuous playback. */
  pause() {
    this.playing = false;
    if (this.timer !== null) {
      clearInterval(this.timer);
      this.timer = null;
    }
  }

  /** Reset cursor to before the first step (does not clear steps). */
  reset() {
    this.pause();
    this.cursor = -1;
    this.updateProgress();
  }

  /** @returns {boolean} Whether there are loaded steps. */
  get hasSteps() {
    return this.steps.length > 0;
  }

  /** @returns {boolean} Whether the cursor is at the last step. */
  get isAtEnd() {
    return this.cursor >= this.steps.length - 1;
  }
}
