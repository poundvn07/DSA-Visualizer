/**
 * modules/algorithms.js — Algorithm module configuration.
 *
 * Provides the display-name mapping and the list of available
 * algorithms for each type (sorting / searching).
 */

const ALGORITHM_CONFIG = {
  sort: {
    quicksort:  { display: 'QuickSort',  complexity: 'O(n log n)' },
    heapsort:   { display: 'HeapSort',   complexity: 'O(n log n)' },
    mergesort:  { display: 'MergeSort',  complexity: 'O(n log n)' },
  },
  search: {
    binarysearch: { display: 'BinarySearch', complexity: 'O(log n)' },
  },
};

/**
 * Get the display name for an algorithm key.
 * @param {string} key — e.g. "quicksort"
 * @returns {string} — e.g. "QuickSort"
 */
function getAlgorithmDisplayName(key) {
  const lower = key.toLowerCase();
  for (const type of Object.values(ALGORITHM_CONFIG)) {
    if (type[lower]) return type[lower].display;
  }
  return key;
}

/**
 * Populate a <select> element with algorithm options for the given type.
 * @param {HTMLSelectElement} selectEl
 * @param {"sort"|"search"} type
 */
function populateAlgorithmSelect(selectEl, type) {
  selectEl.innerHTML = '';
  const algos = ALGORITHM_CONFIG[type] || {};
  for (const [key, info] of Object.entries(algos)) {
    const opt = document.createElement('option');
    opt.value = key;
    opt.textContent = info.display;
    selectEl.appendChild(opt);
  }
}
