/**
 * modules/ds/ds_placeholder.js — Data Structures tab placeholder.
 *
 * Renders a grid of "Coming Soon" cards for future data structure
 * visualisations.  Each card has an emoji icon, name, complexity
 * badge, and a hover lift+glow animation (handled by CSS).
 */

(function () {
  const DS_ITEMS = [
    { icon: '📚', name: 'Stack',        complexity: 'O(1) push/pop' },
    { icon: '🚶', name: 'Queue',        complexity: 'O(1) enq/deq' },
    { icon: '🔗', name: 'Linked List',  complexity: 'O(1) insert'  },
    { icon: '🌳', name: 'Binary Tree',  complexity: 'O(log n) search' },
    { icon: '🕸️', name: 'Graph',        complexity: 'O(V + E) BFS' },
  ];

  const grid = document.getElementById('ds-grid');
  if (!grid) return;

  for (const item of DS_ITEMS) {
    const card = document.createElement('div');
    card.classList.add('ds-card');
    card.innerHTML = `
      <span class="ds-card-icon">${item.icon}</span>
      <span class="ds-card-name">${item.name}</span>
      <span class="ds-card-badge">${item.complexity}</span>
      <span class="ds-card-tag">Coming soon</span>
    `;
    grid.appendChild(card);
  }
})();
