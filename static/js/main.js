/**
 * SNAPBOARD — main.js
 * Global utilities: Indian number format, INR format, toast, date format.
 * Plain ES6, no build tool, no dependencies.
 */

/* ── Indian Number Format ─────────────────────────
 * Converts integer to Indian comma notation.
 * 1234567 → "12,34,567"
─────────────────────────────────────────────────── */
function formatIndianNumber(n) {
  n = Math.round(parseFloat(n));
  if (isNaN(n)) return '0';
  const neg = n < 0;
  let s = String(Math.abs(n));
  if (s.length <= 3) return (neg ? '-' : '') + s;
  let result = s.slice(-3);
  s = s.slice(0, -3);
  while (s.length > 2) {
    result = s.slice(-2) + ',' + result;
    s = s.slice(0, -2);
  }
  if (s) result = s + ',' + result;
  return (neg ? '-' : '') + result;
}

/* ── INR Format ───────────────────────────────────
 * ₹ with Lakh/Crore shorthand (Indian system).
 * 100000   → "₹1.0L"
 * 10000000 → "₹1.0Cr"
 * 1500     → "₹1.5K"
─────────────────────────────────────────────────── */
function formatINR(amount) {
  amount = parseFloat(amount);
  if (isNaN(amount)) return '₹0';
  if (amount >= 1e7)  return `₹${(amount / 1e7).toFixed(1)}Cr`;
  if (amount >= 1e5)  return `₹${(amount / 1e5).toFixed(1)}L`;
  if (amount >= 1e3)  return `₹${(amount / 1e3).toFixed(1)}K`;
  return `₹${formatIndianNumber(amount)}`;
}

/* ── Indian Date Format ───────────────────────────
 * Formats JS Date or ISO string → DD/MM/YYYY
─────────────────────────────────────────────────── */
function formatIndianDate(date) {
  const d = date instanceof Date ? date : new Date(date);
  if (isNaN(d)) return String(date);
  const dd   = String(d.getDate()).padStart(2, '0');
  const mm   = String(d.getMonth() + 1).padStart(2, '0');
  const yyyy = d.getFullYear();
  return `${dd}/${mm}/${yyyy}`;
}

/* ── Chart.js Indian tooltip plugin ──────────────
 * Registers a global plugin so all Chart.js tooltips
 * display ₹ in Indian format automatically.
─────────────────────────────────────────────────── */
if (typeof Chart !== 'undefined') {
  Chart.defaults.plugins.tooltip.callbacks.label = function (context) {
    let label = context.dataset.label || '';
    if (label) label += ': ';
    const val = context.parsed.y ?? context.parsed;
    if (typeof val === 'number') {
      label += formatINR(val);
    } else {
      label += val;
    }
    return label;
  };
}

/* ── Toast notification ───────────────────────────
 * showToast('Message', 'success'|'error'|'info')
─────────────────────────────────────────────────── */
function showToast(message, type = 'info') {
  const existing = document.getElementById('sb-toast');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.id = 'sb-toast';
  Object.assign(toast.style, {
    position:     'fixed',
    bottom:       '24px',
    left:         '50%',
    transform:    'translateX(-50%)',
    background:   type === 'success' ? '#166534'
                : type === 'error'   ? '#7f1d1d'
                :                     '#1e3a5f',
    color:        '#fff',
    padding:      '12px 20px',
    borderRadius: '8px',
    fontSize:     '0.9rem',
    fontWeight:   '600',
    zIndex:       '9999',
    boxShadow:    '0 4px 20px rgba(0,0,0,.5)',
    maxWidth:     '90vw',
    textAlign:    'center',
    transition:   'opacity .3s ease',
  });
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

/* ── Copy to clipboard ────────────────────────────
 * Returns a Promise<boolean>.
─────────────────────────────────────────────────── */
async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    /* Fallback for older browsers */
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    const ok = document.execCommand('copy');
    document.body.removeChild(ta);
    return ok;
  }
}

/* ── Expose globals ─────────────────────────────── */
window.formatIndianNumber = formatIndianNumber;
window.formatINR          = formatINR;
window.formatIndianDate   = formatIndianDate;
window.showToast          = showToast;
window.copyToClipboard    = copyToClipboard;
