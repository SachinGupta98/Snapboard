/**
 * SNAPBOARD — upload.js
 * Handles drag-and-drop / browse file upload, platform detection,
 * Hinglish column mapping preview, GST toggle, and dashboard generation.
 * Plain ES6, no build tool.
 */

(function () {
  'use strict';

  /* ── DOM refs ─────────────────────────────────── */
  const dropZone         = document.getElementById('dropZone');
  const fileInput        = document.getElementById('fileInput');
  const filePreview      = document.getElementById('filePreview');
  const fileName         = document.getElementById('fileName');
  const fileMeta         = document.getElementById('fileMeta');
  const removeFile       = document.getElementById('removeFile');
  const platformTag      = document.getElementById('platformTag');
  const platformIcon     = document.getElementById('platformIcon');
  const platformLabel    = document.getElementById('platformLabel');
  const hinglishNotice   = document.getElementById('hinglishNotice');
  const hinglishList     = document.getElementById('hinglishList');
  const previewSection   = document.getElementById('previewSection');
  const rowCountBadge    = document.getElementById('rowCountBadge');
  const previewTable     = document.getElementById('previewTable');
  const gstToggle        = document.getElementById('gstToggle');
  const gstRateSection   = document.getElementById('gstRateSection');
  const intentBadge      = document.getElementById('intentBadge');
  const intentIcon       = document.getElementById('intentIcon');
  const intentLabel      = document.getElementById('intentLabel');
  const intentDesc       = document.getElementById('intentDesc');
  const generateBtn      = document.getElementById('generateBtn');
  const processingOverlay= document.getElementById('processingOverlay');
  const processingMsg    = document.getElementById('processingMsg');

  let currentDashboardId = null;

  /* ── Platform helpers ─────────────────────────── */
  const PLATFORM_META = {
    razorpay: { icon: '💳', label: 'Razorpay detected' },
    zoho:     { icon: '📋', label: 'Zoho detected' },
    shopify:  { icon: '🛒', label: 'Shopify detected' },
    generic:  { icon: '📊', label: 'Generic CSV / Excel' },
  };

  const INTENT_META = {
    revenue: { icon: '💰', label: 'Revenue Analytics' },
    churn:   { icon: '📉', label: 'Churn Analysis' },
    roas:    { icon: '📣', label: 'ROAS / Marketing' },
    ops:     { icon: '⚙️',  label: 'Operations' },
    mixed:   { icon: '📊', label: 'Mixed Analytics' },
  };

  /* ── Drag & drop ──────────────────────────────── */
  dropZone.addEventListener('click', () => fileInput.click());
  dropZone.addEventListener('dragover', e => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
  });
  dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
  dropZone.addEventListener('drop', e => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  });
  fileInput.addEventListener('change', () => {
    if (fileInput.files[0]) handleFile(fileInput.files[0]);
  });

  /* ── Remove file ──────────────────────────────── */
  removeFile.addEventListener('click', () => {
    fileInput.value = '';
    filePreview.style.display = 'none';
    dropZone.style.display = '';
    currentDashboardId = null;
  });

  /* ── GST toggle ───────────────────────────────── */
  gstToggle.addEventListener('change', () => {
    gstRateSection.style.display = gstToggle.checked ? '' : 'none';
  });

  /* ── File handler ─────────────────────────────── */
  function handleFile(file) {
    const allowedExts = ['csv', 'xlsx', 'xls'];
    const ext = file.name.split('.').pop().toLowerCase();
    if (!allowedExts.includes(ext)) {
      showToast('Please upload a CSV or Excel file (.csv, .xlsx, .xls)', 'error');
      return;
    }
    const sizeMB = file.size / 1024 / 1024;
    if (sizeMB > 10) {
      showToast('File too large. Maximum 10 MB allowed.', 'error');
      return;
    }

    /* Show file name & size */
    fileName.textContent = file.name;
    fileMeta.textContent = `${sizeMB.toFixed(2)} MB · ${ext.toUpperCase()}`;

    dropZone.style.display = 'none';
    filePreview.style.display = '';
    platformTag.style.display = 'none';
    hinglishNotice.style.display = 'none';
    previewSection.style.display = 'none';
    intentBadge.style.display = 'none';
    generateBtn.style.display = 'none';

    uploadAndAnalyse(file);
  }

  /* ── Upload + analyse ─────────────────────────── */
  async function uploadAndAnalyse(file) {
    showProcessing('Uploading and analysing your data…');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res  = await fetch('/upload', { method: 'POST', body: formData });
      const data = await res.json();

      if (!res.ok || data.error) {
        hideProcessing();
        showToast(data.error || 'Upload failed. Please try again.', 'error');
        return;
      }

      currentDashboardId = data.dashboard_id;
      renderAnalysis(data);
    } catch (err) {
      hideProcessing();
      showToast('Network error. Please check your connection.', 'error');
    }
  }

  /* ── Render analysis results ──────────────────── */
  function renderAnalysis(data) {
    hideProcessing();

    /* Platform tag */
    const pm = PLATFORM_META[data.platform] || PLATFORM_META.generic;
    platformIcon.textContent  = pm.icon;
    platformLabel.textContent = pm.label;
    platformTag.style.display = '';

    /* Hinglish columns */
    const hinglishEntries = Object.entries(data.hinglish_detected || {});
    if (hinglishEntries.length > 0) {
      hinglishList.innerHTML = hinglishEntries
        .map(([orig, mapped]) =>
          `<span class="col-badge">${orig} → ${mapped}</span>`)
        .join('');
      hinglishNotice.style.display = '';
    }

    /* Preview table */
    if (data.preview && data.preview.length > 0) {
      const cols = Object.keys(data.preview[0]);
      let html = '<thead><tr>';
      cols.forEach(c => { html += `<th>${c}</th>`; });
      html += '</tr></thead><tbody>';
      data.preview.forEach(row => {
        html += '<tr>';
        cols.forEach(c => { html += `<td>${row[c] ?? ''}</td>`; });
        html += '</tr>';
      });
      html += '</tbody>';
      previewTable.innerHTML = html;
      rowCountBadge.textContent = `${data.row_count.toLocaleString('en-IN')} rows`;
      previewSection.style.display = '';
    }

    /* Intent badge */
    const im = INTENT_META[data.intent] || INTENT_META.revenue;
    intentIcon.textContent  = im.icon;
    intentLabel.textContent = im.label;
    intentDesc.textContent  = data.description || '';
    intentBadge.style.display = '';

    /* Generate button */
    generateBtn.style.display = '';
    generateBtn.onclick = () => {
      window.location.href = `/dashboard/${currentDashboardId}`;
    };
  }

  /* ── Processing overlay ───────────────────────── */
  function showProcessing(msg) {
    processingMsg.textContent = msg || 'Analysing…';
    processingOverlay.style.display = '';
  }
  function hideProcessing() {
    processingOverlay.style.display = 'none';
  }

})();
