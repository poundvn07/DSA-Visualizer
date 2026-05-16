/**
 * bridge.js — Main application controller.
 *
 * Initialises all modules (Renderer, StateManager, PseudocodePanel,
 * StatsPanel), wires DOM event listeners, and orchestrates
 * communication between the JavaScript UI and the Python backend
 * via eel.
 *
 * Navigation: Landing page → Visualizer (via card click) → Back
 */

(function () {
  'use strict';

  // ── Module instances ───────────────────────────────────────────
  const renderer = new Renderer('viz-canvas');
  const state = new StateManager();
  const pseudocode = new PseudocodePanel('pseudocode-lines');
  const stats = new StatsPanel();

  // ── DOM references ─────────────────────────────────────────────
  const sizeSlider = document.getElementById('size-slider');
  const sizeValue = document.getElementById('size-value');
  const speedSlider = document.getElementById('speed-slider');
  const speedValue = document.getElementById('speed-value');
  const algoSelect = document.getElementById('algo-select');
  const statusLabel = document.getElementById('status-label');
  const nlExplain = document.getElementById('nl-explanation');

  const btnNew = document.getElementById('btn-new');
  const btnStepBack = document.getElementById('btn-step-back');
  const btnPlay = document.getElementById('btn-play');
  const btnStepFwd = document.getElementById('btn-step-fwd');
  const btnReset = document.getElementById('btn-reset');
  const btnHelp = document.getElementById('btn-help');

  const typeToggle = document.getElementById('type-toggle');
  const searchGroup = document.getElementById('search-target-group');
  const searchTargetEl = document.getElementById('search-target');
  const statSearchRows = document.querySelectorAll('.stat-search-row');
  const statSwapsRow = document.getElementById('stat-row-swaps');
  const statTarget = document.getElementById('stat-target');
  const statLow = document.getElementById('stat-low');
  const statMid = document.getElementById('stat-mid');
  const statHigh = document.getElementById('stat-high');

  const helpModal = document.getElementById('help-modal');
  const helpClose = document.getElementById('help-close');

  // Views
  const viewHome = document.getElementById('view-home');
  const viewAlgo = document.getElementById('view-algorithms');
  const viewDS = document.getElementById('view-ds');
  const btnBackHome = document.getElementById('btn-back-home');

  // Pivot strategy
  const pivotGroup = document.getElementById('pivot-group');
  const pivotSelect = document.getElementById('pivot-select');

  // Custom input
  const customInput = document.getElementById('custom-input');
  const btnApplyCustom = document.getElementById('btn-apply-custom');
  const vizCanvas = document.getElementById('viz-canvas');

  // Theme toggle
  const themeToggle = document.getElementById('theme-toggle');

  // ── Application state ──────────────────────────────────────────
  let currentType = 'sort';       // 'sort' | 'search'
  let currentArray = [];          // the initial (unsorted) array
  let stepsLoaded = false;

  // ── Algorithm display name lookup ──────────────────────────────
  const DISPLAY_NAMES = {
    quicksort: 'QuickSort',
    heapsort: 'HeapSort',
    mergesort: 'MergeSort',
    binarysearch: 'BinarySearch',
  };

  // ── Helpers ────────────────────────────────────────────────────

  function getDelay() {
    const mult = parseFloat(speedSlider.value);
    return Math.floor(100 / mult);
  }

  function getSize() {
    return parseInt(sizeSlider.value, 10);
  }

  function getInputType() {
    const active = document.querySelector('#input-type-chips .chip.active');
    return active ? active.dataset.value : 'random';
  }

  function getAlgorithm() {
    return algoSelect.value;
  }

  function getDisplayName() {
    return DISPLAY_NAMES[getAlgorithm()] || getAlgorithm();
  }

  function showLoading() {
    let overlay = document.querySelector('.canvas-loading');
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.classList.add('canvas-loading');
      overlay.textContent = '⏳ Computing steps…';
      document.getElementById('canvas-section').appendChild(overlay);
    }
  }

  function hideLoading() {
    const overlay = document.querySelector('.canvas-loading');
    if (overlay) overlay.remove();
  }

  function setFooterStatus(text) {
    if (statusLabel) statusLabel.textContent = text;
  }

  function resetSearchStats() {
    if (statTarget) statTarget.textContent = searchTargetEl.value || '—';
    if (statLow) statLow.textContent = '—';
    if (statMid) statMid.textContent = '—';
    if (statHigh) statHigh.textContent = '—';
  }

  function setStatsMode(type) {
    statSearchRows.forEach(row => row.classList.toggle('hidden', type !== 'search'));
    if (statSwapsRow) statSwapsRow.classList.toggle('hidden', type === 'search');
    resetSearchStats();
  }

  function updateSearchStats(step = null) {
    if (currentType !== 'search') return;
    if (statTarget) statTarget.textContent = searchTargetEl.value || '—';

    if (step?.type === 'range' && step.indices.length === 3) {
      const [low, mid, high] = step.indices;
      if (statLow) statLow.textContent = low;
      if (statMid) statMid.textContent = mid;
      if (statHigh) statHigh.textContent = high;
    } else if (step?.indices?.length) {
      if (statMid) statMid.textContent = step.indices[0];
    } else if (step?.type === 'not_found') {
      if (statLow) statLow.textContent = '—';
      if (statMid) statMid.textContent = '—';
      if (statHigh) statHigh.textContent = '—';
    }
  }

  function setStepFooter(current, total) {
    const target = currentType === 'search' && searchTargetEl.value
      ? ` · target ${searchTargetEl.value}`
      : '';
    setFooterStatus(`${getDisplayName()} · Step ${current} / ${total}${target}`);
  }

  function algorithmPlaybackAdapter() {
    return {
      animateStep: (step) => {
        renderer.animateStep(step);
        pseudocode.highlightLine(step.highlight_line);
        stats.update(step, state.cursor + 1, state.steps.length);
        updateSearchStats(step);
        setStepFooter(state.cursor + 1, state.steps.length);
      },
      completedSweep: (arrayState, step) => {
        if (currentType === 'sort') {
          renderer.completedSweep(arrayState);
        } else if (currentType === 'search' && step && step.type === 'not_found') {
          renderer.completedSweep(arrayState, 'not_found');
        }
      },
    };
  }

  function setPlayButton(playing) {
    if (playing) {
      btnPlay.innerHTML = '<svg class="icon-line" viewBox="0 0 24 24"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg><span>Pause</span>';
      btnPlay.classList.add('paused');
    } else {
      btnPlay.innerHTML = '<svg class="icon-line" viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg><span>Play</span>';
      btnPlay.classList.remove('paused');
    }
  }

  /** Clear the NL explanation line. */
  function clearExplanation() {
    if (nlExplain) {
      nlExplain.textContent = '';
      nlExplain.style.color = '';
    }
  }

  function redrawAlgorithmCanvasForTheme() {
    const currentStep = state.cursor >= 0 ? state.steps[state.cursor] : null;
    if (currentStep) {
      renderer.animateStep(currentStep);
    } else if (currentArray.length > 0) {
      renderer.drawArray(currentArray, {});
    } else {
      renderer.clear();
    }
  }

  function redrawDsCanvasForTheme() {
    const currentStep = dsState.cursor >= 0 ? dsState.steps[dsState.cursor] : dsRenderer._lastStep;
    if (currentStep) {
      dsRenderer.drawStep(currentStep);
    } else {
      dsRenderer.clear(currentDsType);
    }
  }

  // ── View Navigation ────────────────────────────────────────────

  /**
   * Navigate to the algorithm visualizer with the given type.
   * @param {'sort'|'search'} type
   */
  function navigateToVisualizer(type) {
    currentType = type;

    // Update the type toggle to match.
    typeToggle.querySelectorAll('.toggle-btn').forEach(b => {
      b.classList.toggle('active', b.dataset.value === type);
    });

    // Populate algorithm dropdown for the type.
    populateAlgorithmSelect(algoSelect, type);

    // Show/hide search target.
    if (type === 'search') {
      searchGroup.classList.remove('hidden');
    } else {
      searchGroup.classList.add('hidden');
    }
    setStatsMode(type);

    updatePivotVisibility();

    // Switch views.
    viewHome.classList.remove('active');
    viewAlgo.classList.add('active');

    // Trigger initial array generation.
    onNew();
  }

  function navigateToHome() {
    // Stop any animation.
    state.pause();
    setPlayButton(false);

    viewAlgo.classList.remove('active');
    viewDS.classList.remove('active');
    viewHome.classList.add('active');
  }

  // ── Home page card clicks ──────────────────────────────────────

  document.querySelectorAll('.home-card[data-navigate]').forEach(card => {
    card.addEventListener('click', () => {
      const target = card.dataset.navigate;
      navigateToVisualizer(target);
    });
  });

  // ── Smooth Scrolling for Nav & Hero ────────────────────────────
  document.querySelectorAll('[data-scroll-to]').forEach(el => {
    el.addEventListener('click', (e) => {
      e.preventDefault();
      const targetId = el.getAttribute('data-scroll-to');
      const targetEl = document.querySelector(targetId);
      if (targetEl) {
        targetEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  if (btnBackHome) {
    btnBackHome.addEventListener('click', navigateToHome);
  }

  // ── Theme Toggle ───────────────────────────────────────────────

  function updateThemeIcon(theme) {
    const themeIcon = document.querySelector('#theme-toggle svg');
    if (themeIcon) {
      if (theme === 'light') {
        themeIcon.innerHTML = '<circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>';
      } else {
        themeIcon.innerHTML = '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>';
      }
    }
  }

  function initTheme() {
    let saved = localStorage.getItem('dsa-theme');
    if (!saved) {
      saved = 'dark';
      localStorage.setItem('dsa-theme', 'dark');
    }
    document.documentElement.setAttribute('data-theme', saved);
    updateThemeIcon(saved);
  }

  function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('dsa-theme', next);
    updateThemeIcon(next);

    // Redraw canvases with the exact frame currently shown.
    redrawAlgorithmCanvasForTheme();
    redrawDsCanvasForTheme();

    // Re-render legend with new colours.
    const algo = getAlgorithm();
    renderLegend(algo);
  }

  if (themeToggle) {
    themeToggle.addEventListener('click', toggleTheme);
  }

  // ── Core actions ───────────────────────────────────────────────

  /**
   * Generate a new array from Python, render it, load pseudo-code.
   */
  async function onNew() {
    state.pause();
    setPlayButton(false);
    stepsLoaded = false;
    clearExplanation();

    const size = getSize();
    const inputType = getInputType();

    try {
      currentArray = await eel.generate_array(size, inputType)();
    } catch (err) {
      statusLabel.textContent = 'Error generating array: ' + err;
      return;
    }

    if (currentType === 'search') {
      currentArray.sort((a, b) => a - b);
    }

    renderer.drawArray(currentArray);
    setFooterStatus('Array loaded — ready to visualize');

    const algo = getAlgorithm();
    try {
      const lines = await eel.get_pseudocode(algo)();
      pseudocode.load(lines);
    } catch (_) {
      pseudocode.clear();
    }

    stats.reset();
    stats.setAlgorithm(getDisplayName(), algo);
    stats.setN(size);
    resetSearchStats();

    state.load([]);
  }

  /**
   * Fetch all steps from Python for the current algorithm + array.
   */
  async function ensureSteps() {
    if (stepsLoaded && state.hasSteps) return;

    showLoading();

    const algo = getAlgorithm();
    let steps;

    try {
      if (currentType === 'sort') {
        const options = algo === 'quicksort'
          ? { pivot_strategy: pivotSelect.value }
          : {};
        steps = await eel.get_sort_steps(currentArray, algo, options)();
      } else {
        let target = parseInt(searchTargetEl.value, 10);
        if (isNaN(target)) {
          const sorted = [...currentArray].sort((a, b) => a - b);
          target = sorted[Math.floor(Math.random() * sorted.length)];
          searchTargetEl.value = target;
        }
        updateSearchStats();
        currentArray = [...currentArray].sort((a, b) => a - b);
        renderer.drawArray(currentArray);
        steps = await eel.get_search_steps(currentArray, target)();
      }
    } catch (err) {
      hideLoading();
      setFooterStatus('Error computing steps: ' + err);
      return;
    }

    hideLoading();
    state.load(steps);
    stepsLoaded = true;
  }

  /**
   * Apply one step to all visual panels.
   */
  function applyStep(step) {
    if (!step) return;
    renderer.animateStep(step);
    pseudocode.highlightLine(step.highlight_line);
    stats.update(step, state.cursor + 1, state.steps.length);
    updateSearchStats(step);
    setStepFooter(state.cursor + 1, state.steps.length);
    
    btnStepBack.disabled = state.cursor <= 0;

    if (state.cursor === state.steps.length - 1) {
      if (currentType === 'sort') {
        renderer.completedSweep(step.array_state);
      } else if (currentType === 'search' && step.type === 'not_found') {
        renderer.completedSweep(step.array_state, 'not_found');
      }
    }
  }

  // ── Button handlers ────────────────────────────────────────────

  btnNew.addEventListener('click', onNew);

  btnStepFwd.addEventListener('click', async () => {
    state.pause();
    setPlayButton(false);
    await ensureSteps();
    const step = state.stepForward();
    applyStep(step);
  });

  btnStepBack.addEventListener('click', () => {
    state.pause();
    setPlayButton(false);
    const step = state.stepBackward();
    applyStep(step);
  });

  btnPlay.addEventListener('click', async () => {
    if (state.playing) {
      state.pause();
      setPlayButton(false);
      setFooterStatus(`Paused — ${getDisplayName()}`);
      return;
    }

    await ensureSteps();
    if (!state.hasSteps) return;

    if (state.isAtEnd) {
      state.reset();
      renderer.drawArray(currentArray);
      pseudocode.reset();
      clearExplanation();
    }

    setPlayButton(true);
    setFooterStatus(`Playing ${getDisplayName()}...`);
    state.play(algorithmPlaybackAdapter(), stats, pseudocode, getDelay(), () => {
      setPlayButton(false);
      setFooterStatus(state.isAtEnd
        ? `Completed — ${getDisplayName()}`
        : `Paused — ${getDisplayName()}`);
    });
  });

  btnReset.addEventListener('click', () => {
    state.pause();
    state.reset();
    setPlayButton(false);
    stepsLoaded = false;
    clearExplanation();

    renderer.drawArray(currentArray);
    setFooterStatus('Reset — ready to visualize');
    pseudocode.reset();
    stats.reset();
    stats.setAlgorithm(getDisplayName(), getAlgorithm());
    stats.setN(getSize());
    resetSearchStats();
  });

  // ── Slider listeners ──────────────────────────────────────────

  sizeSlider.addEventListener('input', () => {
    sizeValue.textContent = sizeSlider.value;
  });

  speedSlider.addEventListener('input', () => {
    const el = speedValue;
    const mult = parseFloat(speedSlider.value);
    const delay = Math.floor(100 / mult);
    el.innerHTML = `${mult.toFixed(1)}x<div class="tooltip-box">${delay} ms per step</div>`;

    if (state.playing) {
      state.pause();
      state.play(algorithmPlaybackAdapter(), stats, pseudocode, getDelay(), () => {
        setPlayButton(false);
        setFooterStatus(state.isAtEnd
          ? `Completed — ${getDisplayName()}`
          : `Paused — ${getDisplayName()}`);
      });
    }
  });

  // ── Chip selector for Input Type ───────────────────────────────

  document.querySelectorAll('#input-type-chips .chip').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('#input-type-chips .chip')
        .forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    });
  });

  // ── Type toggle (Sorting ↔ Searching) inside visualizer ────────

  typeToggle.addEventListener('click', (e) => {
    const btn = e.target.closest('.toggle-btn');
    if (!btn) return;

    const value = btn.dataset.value;
    if (value === currentType) return;

    currentType = value;

    typeToggle.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    populateAlgorithmSelect(algoSelect, currentType);

    if (currentType === 'search') {
      searchGroup.classList.remove('hidden');
    } else {
      searchGroup.classList.add('hidden');
    }
    setStatsMode(currentType);

    updatePivotVisibility();
    onNew();
  });

  // ── Algorithm change ───────────────────────────────────────────

  algoSelect.addEventListener('change', async () => {
    stepsLoaded = false;
    state.load([]);
    state.pause();
    setPlayButton(false);
    clearExplanation();

    const algo = getAlgorithm();
    try {
      const lines = await eel.get_pseudocode(algo)();
      pseudocode.load(lines);
    } catch (_) {
      pseudocode.clear();
    }

    stats.reset();
    stats.setAlgorithm(getDisplayName(), algo);
    stats.setN(getSize());
    setStatsMode(currentType);
    setFooterStatus('Algorithm changed — click New or Play');

    updatePivotVisibility();
  });

  // ── Pivot strategy visibility ──────────────────────────────────

  function updatePivotVisibility() {
    if (pivotGroup) {
      pivotGroup.style.display =
        (currentType === 'sort' && getAlgorithm() === 'quicksort')
          ? 'flex' : 'none';
    }
  }

  // ── Custom Array Input ─────────────────────────────────────────

  btnApplyCustom.addEventListener('click', () => {
    const raw = customInput.value;
    const nums = raw.split(',')
      .map(s => parseInt(s.trim(), 10))
      .filter(n => !isNaN(n));

    if (nums.length < 2) {
      customInput.classList.add('error');
      return;
    }
    customInput.classList.remove('error');

    currentArray = nums;
    renderer.drawArray(nums, {});
    state.reset();
    stepsLoaded = false;
    clearExplanation();
    setFooterStatus(`Custom array loaded (${nums.length} elements)`);
    stats.reset();
    stats.setAlgorithm(getDisplayName(), getAlgorithm());
    stats.setN(nums.length);
    resetSearchStats();
    sizeSlider.value = Math.min(200, Math.max(5, nums.length));
    sizeValue.textContent = sizeSlider.value;
  });

  // ── Bar click editor (idle mode only) ──────────────────────────

  vizCanvas.addEventListener('click', (e) => {
    if (state.playing || state.hasSteps) return;
    if (currentArray.length === 0) return;

    const idx = renderer.hitTestBar(e.clientX);
    if (idx < 0 || idx >= currentArray.length) return;

    const newVal = parseInt(
      prompt(`Edit value at index ${idx} (current: ${currentArray[idx]})`),
      10
    );
    if (!isNaN(newVal) && newVal > 0) {
      currentArray[idx] = newVal;
      renderer.drawArray(currentArray, {});
    }
  });

  // ── Bar hover highlight (idle mode only) ───────────────────────

  vizCanvas.addEventListener('mousemove', (e) => {
    if (state.playing || state.hasSteps) {
      vizCanvas.style.cursor = 'default';
      return;
    }
    if (currentArray.length === 0) return;

    const idx = renderer.hitTestBar(e.clientX);
    if (idx >= 0 && idx < currentArray.length) {
      vizCanvas.style.cursor = 'pointer';
      const highlights = {};
      highlights[idx] = 'hover';
      renderer.drawArray(currentArray, highlights);
    } else {
      vizCanvas.style.cursor = 'default';
      renderer.drawArray(currentArray, {});
    }
  });

  vizCanvas.addEventListener('mouseleave', () => {
    if (!state.playing && !state.hasSteps && currentArray.length > 0) {
      renderer.drawArray(currentArray, {});
    }
    vizCanvas.style.cursor = 'default';
  });

  // ── Help modal ─────────────────────────────────────────────────

  btnHelp.addEventListener('click', () => {
    helpModal.classList.remove('hidden');
  });
  helpClose.addEventListener('click', () => {
    helpModal.classList.add('hidden');
  });
  helpModal.addEventListener('click', (e) => {
    if (e.target === helpModal) helpModal.classList.add('hidden');
  });

  // ── DS Visualizer Module ────────────────────────────────────────

  const dsRenderer = new DSRenderer('ds-canvas');
  const dsPseudocode = new PseudocodePanel('ds-pseudocode-lines');
  const dsState = new StateManager();

  const dsValueInput = document.getElementById('ds-value-input');
  const dsOpButtons = document.getElementById('ds-op-buttons');
  const dsPanelTitle = document.getElementById('ds-panel-title');
  const dsStatusLabel = document.getElementById('ds-status-label');
  const btnDsBackHome = document.getElementById('btn-ds-back-home');
  const btnDsClear = document.getElementById('btn-ds-clear');
  const btnDsStepBack = document.getElementById('btn-ds-step-back');
  const btnDsPlay = document.getElementById('btn-ds-play');
  const btnDsStepFwd = document.getElementById('btn-ds-step-fwd');
  const btnDsReset = document.getElementById('btn-ds-reset');
  const dsSpeedSlider = document.getElementById('ds-speed-slider');
  const dsSpeedValue = document.getElementById('ds-speed-value');

  let currentDsType = 'stack';
  let dsOperations = [];       // accumulated operations list
  let dsStepsLoaded = false;

  const DS_DISPLAY = {
    stack: 'Stack', queue: 'Queue',
    linkedlist: 'Linked List', bst: 'Binary Search Tree',
  };

  const DS_OPS = {
    stack: [['Push', 'push', true], ['Pop', 'pop', false], ['Peek', 'peek', false]],
    queue: [['Enqueue', 'enqueue', true], ['Dequeue', 'dequeue', false], ['Peek', 'peek', false]],
    linkedlist: [['Insert Head', 'insert_head', true], ['Insert Tail', 'insert_tail', true],
    ['Delete', 'delete', true], ['Search', 'search', true]],
    bst: [['Insert', 'insert', true], ['Search', 'search', true], ['Inorder', 'inorder', false]],
  };

  function populateDsOpButtons(dsType) {
    dsOpButtons.innerHTML = '';
    const ops = DS_OPS[dsType] || [];
    for (const [label, op, needsVal] of ops) {
      const btn = document.createElement('button');
      btn.className = 'ds-op-btn';
      btn.textContent = label;
      btn.addEventListener('click', () => dsRunOp(op, needsVal));
      dsOpButtons.appendChild(btn);
    }
  }

  async function dsRunOp(op, needsVal) {
    let value = null;
    if (needsVal) {
      value = parseInt(dsValueInput.value, 10);
      if (isNaN(value)) {
        dsStatusLabel.textContent = '⚠ Nhập một số nguyên trước!';
        dsValueInput.focus();
        return;
      }
    }

    const opObj = needsVal ? { op, value } : { op };
    dsOperations.push(opObj);

    // Fetch all steps for the full operation history.
    try {
      const oldLength = dsState.steps.length;
      const steps = await eel.get_ds_steps(currentDsType, dsOperations)();

      // Stop any current animation before loading new steps
      if (dsState.playing) {
        btnDsPlay.click(); // This will pause it
      }

      dsState.load(steps);
      dsStepsLoaded = true;

      // Update basic stats immediately
      const elType = document.getElementById('ds-stat-type');
      const elOps = document.getElementById('ds-stat-ops');
      if (elType) elType.textContent = DS_DISPLAY[currentDsType];
      if (elOps) elOps.textContent = dsOperations.length;

      // Restore cursor to the end of the *previous* operations
      // so we can play the animation for the *new* operation.
      dsState.cursor = oldLength > 0 ? oldLength - 1 : -1;
      dsState.updateProgress();

      // Automatically play the new steps
      if (!dsState.playing) {
        btnDsPlay.click();
      }

    } catch (err) {
      dsStatusLabel.textContent = 'Error: ' + err;
    }

    dsValueInput.value = '';
    dsValueInput.focus();
  }

  function dsApplyStep(step) {
    if (!step) return;
    dsRenderer.drawStep(step);
    dsStatusLabel.textContent = step.description;
    dsPseudocode.highlightLine(step.highlight_line);
    const elStep = document.getElementById('ds-stat-step');
    if (elStep) elStep.textContent = `${dsState.cursor + 1} / ${dsState.steps.length}`;
    const elSize = document.getElementById('ds-stat-size');
    if (elSize) elSize.textContent = step.array_state.length;
    btnDsStepBack.disabled = dsState.cursor <= 0;
  }

  if (dsSpeedSlider) {
    dsSpeedSlider.addEventListener('input', () => {
      const mult = parseFloat(dsSpeedSlider.value);
      const delay = Math.floor(250 / mult);
      dsSpeedValue.innerHTML = `${mult.toFixed(1)}x<div class="tooltip-box">${delay} ms per step</div>`;
      if (dsState.playing) {
        // We need to re-play with the new delay
        dsState.pause();
        dsState.play(dsRenderer, null, dsPseudocode, delay, () => {
          btnDsPlay.innerHTML = '<svg class="icon-line" viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg><span>Play</span>';
          btnDsPlay.classList.remove('paused');
        });
      }
    });
  }

  // DS playback controls
  btnDsStepFwd.addEventListener('click', () => {
    dsState.pause();
    dsApplyStep(dsState.stepForward());
  });
  btnDsStepBack.addEventListener('click', () => {
    dsState.pause();
    dsApplyStep(dsState.stepBackward());
  });
  btnDsPlay.addEventListener('click', () => {
    if (dsState.playing) {
      dsState.pause();
      btnDsPlay.innerHTML = '<svg class="icon-line" viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg><span>Play</span>';
      btnDsPlay.classList.remove('paused');
      return;
    }
    if (!dsState.hasSteps) return;
    if (dsState.isAtEnd) dsState.reset();
    btnDsPlay.innerHTML = '<svg class="icon-line" viewBox="0 0 24 24"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg><span>Pause</span>';
    btnDsPlay.classList.add('paused');
    dsState.play(
      { animateStep: (s) => dsRenderer.drawStep(s), completedSweep: () => { } },
      {
        update: (s, c, t) => {
          dsStatusLabel.textContent = s.description;
          const el = document.getElementById('ds-stat-step');
          if (el) el.textContent = `${c} / ${t}`;
          const elSize = document.getElementById('ds-stat-size');
          if (elSize) elSize.textContent = s.array_state.length;
        }
      },
      dsPseudocode, Math.floor(250 / parseFloat(dsSpeedSlider.value)), () => {
        btnDsPlay.innerHTML = '<svg class="icon-line" viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg><span>Play</span>';
        btnDsPlay.classList.remove('paused');
      }
    );
  });
  btnDsReset.addEventListener('click', () => {
    dsState.pause();
    dsState.reset();
    dsRenderer.clear(currentDsType);
    dsStatusLabel.textContent = 'Ready — choose an operation';
    btnDsPlay.innerHTML = '<svg class="icon-line" viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg><span>Play</span>';
    btnDsPlay.classList.remove('paused');
  });
  btnDsClear.addEventListener('click', () => {
    dsOperations = [];
    dsState.load([]);
    dsStepsLoaded = false;
    dsRenderer.clear(currentDsType);
    dsStatusLabel.textContent = DS_DISPLAY[currentDsType] + ' cleared';
    const elSize = document.getElementById('ds-stat-size');
    const elOps = document.getElementById('ds-stat-ops');
    if (elSize) elSize.textContent = '0';
    if (elOps) elOps.textContent = '0';
  });

  // DS card navigation from home
  document.querySelectorAll('.home-card[data-navigate-ds]').forEach(card => {
    card.addEventListener('click', () => {
      currentDsType = card.dataset.navigateDs;
      navigateToDsVisualizer(currentDsType);
    });
  });

  async function navigateToDsVisualizer(dsType) {
    viewHome.classList.remove('active');
    viewAlgo.classList.remove('active');
    viewDS.classList.add('active');

    const titleTextEl = document.getElementById('ds-panel-title-text');
    if (titleTextEl) titleTextEl.textContent = DS_DISPLAY[dsType] || dsType;
    populateDsOpButtons(dsType);
    dsOperations = [];
    dsState.load([]);
    dsRenderer.clear(dsType);
    dsStatusLabel.textContent = 'Ready — choose an operation';

    // Load pseudocode
    try {
      const lines = await eel.get_ds_pseudocode(dsType)();
      dsPseudocode.load(lines);
    } catch (_) {
      dsPseudocode.clear();
    }

    const elType = document.getElementById('ds-stat-type');
    if (elType) elType.textContent = DS_DISPLAY[dsType];
  }

  if (btnDsBackHome) {
    btnDsBackHome.addEventListener('click', () => {
      dsState.pause();
      viewDS.classList.remove('active');
      viewHome.classList.add('active');
    });
  }

  // ── Keyboard shortcuts ─────────────────────────────────────────

  document.addEventListener('keydown', (e) => {
    if (document.activeElement.tagName === 'INPUT' ||
      document.activeElement.tagName === 'SELECT') return;

    const inVisualizer = viewAlgo.classList.contains('active');
    const inDS = viewDS.classList.contains('active');

    switch (e.key) {
      case ' ':
        if (inVisualizer) { e.preventDefault(); btnPlay.click(); }
        if (inDS) { e.preventDefault(); btnDsPlay.click(); }
        break;
      case 'ArrowRight':
        if (inVisualizer) { e.preventDefault(); btnStepFwd.click(); }
        if (inDS) { e.preventDefault(); btnDsStepFwd.click(); }
        break;
      case 'ArrowLeft':
        if (inVisualizer) { e.preventDefault(); btnStepBack.click(); }
        if (inDS) { e.preventDefault(); btnDsStepBack.click(); }
        break;
      case 'n':
        if (inVisualizer) btnNew.click();
        break;
      case 'r':
        if (inVisualizer) btnReset.click();
        if (inDS) btnDsReset.click();
        break;
      case 'd':
        toggleTheme();
        break;
      case 'Escape':
        if (inVisualizer || inDS) navigateToHome();
        break;
    }
  });

  // ── Initialise on load ─────────────────────────────────────────

  initTheme();

})();
