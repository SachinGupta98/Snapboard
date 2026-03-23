/**
 * SNAPBOARD — charts.js
 * Chart.js helper functions with India-first formatting.
 * All tooltips show ₹ in Indian Lakh/Crore format.
 * Plain ES6, no build tool.
 */

/* ── Shared Chart.js defaults ─────────────────────
 * Applied once when this file loads.
─────────────────────────────────────────────────── */
Chart.defaults.color            = '#9090B0';
Chart.defaults.borderColor      = '#2A2A4A';
Chart.defaults.font.family      = "'Inter', system-ui, sans-serif";
Chart.defaults.font.size        = 12;
Chart.defaults.plugins.legend.position = 'bottom';
Chart.defaults.plugins.legend.labels.padding = 16;
Chart.defaults.plugins.legend.labels.usePointStyle = true;

/* ── Indian tooltip callback ──────────────────────
 * Overrides the default Chart.js tooltip to show
 * ₹ amounts in Indian Lakh/Crore notation.
─────────────────────────────────────────────────── */
const INDIAN_TOOLTIP = {
  callbacks: {
    label(context) {
      const ds    = context.dataset.label || '';
      const raw   = context.parsed.y ?? context.parsed;
      const label = ds ? `${ds}: ` : '';
      if (typeof raw === 'number') {
        return label + window.formatINR(raw);
      }
      return label + raw;
    },
  },
};

/* ── Colour palette ───────────────────────────────
 * Saffron-centric with gold, green accents.
─────────────────────────────────────────────────── */
const PALETTE = [
  '#FF6B35', // saffron
  '#F7B731', // gold
  '#22c55e', // green
  '#60a5fa', // blue
  '#a78bfa', // purple
  '#fb923c', // amber
  '#f472b6', // pink
  '#34d399', // teal
];

function paletteColor(i) {
  return PALETTE[i % PALETTE.length];
}

/* ── Shared options builder ───────────────────────
 * Returns Chart.js options common to all chart types.
─────────────────────────────────────────────────── */
function sharedOptions(extra = {}) {
  return {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 600 },
    plugins: {
      tooltip: INDIAN_TOOLTIP,
      ...extra.plugins,
    },
    ...extra,
  };
}

/* ─────────────────────────────────────────────────
   CHART FACTORY FUNCTIONS
─────────────────────────────────────────────────── */

/**
 * buildMonthlyChart — Bar or line chart of monthly revenue.
 * @param {string} canvasId
 * @param {Array}  data      — [{month, revenue}, ...]
 * @param {string} [type]    — 'bar' | 'line'
 * @returns {Chart}
 */
function buildMonthlyChart(canvasId, data, type = 'bar') {
  const labels   = data.map(d => d.month);
  const revenues = data.map(d => d.revenue);

  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;

  return new Chart(ctx, {
    type,
    data: {
      labels,
      datasets: [{
        label:                'Monthly Revenue',
        data:                 revenues,
        backgroundColor:      type === 'bar'
          ? revenues.map((_, i) => paletteColor(i) + 'CC')
          : 'rgba(255,107,53,.15)',
        borderColor:          type === 'bar'
          ? revenues.map((_, i) => paletteColor(i))
          : '#FF6B35',
        borderWidth:          type === 'bar' ? 1 : 2,
        fill:                 type === 'line',
        tension:              0.35,
        pointBackgroundColor: '#FF6B35',
        pointRadius:          type === 'line' ? 4 : 0,
      }],
    },
    options: sharedOptions({
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: v => window.formatINR(v),
          },
        },
        x: { grid: { display: false } },
      },
    }),
  });
}

/**
 * buildDailyChart — Area line chart for last-30-days revenue.
 * @param {string} canvasId
 * @param {Array}  data   — [{day, revenue}, ...]
 * @returns {Chart}
 */
function buildDailyChart(canvasId, data) {
  const labels   = data.map(d => d.day);
  const revenues = data.map(d => d.revenue);

  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;

  return new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label:                'Daily Revenue',
        data:                 revenues,
        backgroundColor:      'rgba(247,183,49,.12)',
        borderColor:          '#F7B731',
        borderWidth:          2,
        fill:                 true,
        tension:              0.4,
        pointRadius:          2,
        pointBackgroundColor: '#F7B731',
      }],
    },
    options: sharedOptions({
      scales: {
        y: {
          beginAtZero: true,
          ticks: { callback: v => window.formatINR(v) },
        },
        x: {
          ticks: {
            maxTicksLimit: 7,
            maxRotation:   0,
          },
          grid: { display: false },
        },
      },
    }),
  });
}

/**
 * buildProductsChart — Horizontal bar chart for top products.
 * @param {string} canvasId
 * @param {Array}  data   — [{name, revenue}, ...]
 * @returns {Chart}
 */
function buildProductsChart(canvasId, data) {
  const labels   = data.map(d => d.name);
  const revenues = data.map(d => d.revenue);

  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;

  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label:           'Revenue',
        data:            revenues,
        backgroundColor: labels.map((_, i) => paletteColor(i) + 'CC'),
        borderColor:     labels.map((_, i) => paletteColor(i)),
        borderWidth:     1,
        borderRadius:    4,
      }],
    },
    options: sharedOptions({
      indexAxis: 'y',
      scales: {
        x: {
          beginAtZero: true,
          ticks: { callback: v => window.formatINR(v) },
        },
        y: { grid: { display: false } },
      },
      plugins: {
        legend: { display: false },
        tooltip: INDIAN_TOOLTIP,
      },
    }),
  });
}

/**
 * buildCitiesChart — Doughnut chart for revenue by city.
 * @param {string} canvasId
 * @param {Array}  data   — [{city, revenue}, ...]
 * @returns {Chart}
 */
function buildCitiesChart(canvasId, data) {
  const labels   = data.map(d => d.city);
  const revenues = data.map(d => d.revenue);

  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;

  return new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        label:           'Revenue',
        data:            revenues,
        backgroundColor: labels.map((_, i) => paletteColor(i) + 'CC'),
        borderColor:     '#1A1A2E',
        borderWidth:     2,
        hoverOffset:     6,
      }],
    },
    options: sharedOptions({
      cutout: '65%',
      plugins: {
        legend: { position: 'right' },
        tooltip: {
          callbacks: {
            label(ctx) {
              const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
              const pct   = ((ctx.parsed / total) * 100).toFixed(1);
              return `${ctx.label}: ${window.formatINR(ctx.parsed)} (${pct}%)`;
            },
          },
        },
      },
    }),
  });
}

/* ── Expose chart builders globally ─────────────── */
window.buildMonthlyChart  = buildMonthlyChart;
window.buildDailyChart    = buildDailyChart;
window.buildProductsChart = buildProductsChart;
window.buildCitiesChart   = buildCitiesChart;
window.paletteColor       = paletteColor;
