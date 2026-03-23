/**
 * SNAPBOARD — dashboard.js
 * Initialises all charts, handles GST toggle, NL chat, share,
 * WhatsApp digest modal, and chart-type switching.
 * Plain ES6, no build tool.
 * Depends on: charts.js (chart builders), main.js (formatINR, showToast)
 */

(function () {
  'use strict';

  /* ── Injected from Jinja2 ─────────────────────── */
  const dashId   = window.DASHBOARD_ID   || '';
  const metrics  = window.DASHBOARD_METRICS || {};

  /* ── Chart instances (kept for type-switching) ── */
  const chartInstances = {};

  /* ════════════════════════════════════════════════
     INIT CHARTS
  ════════════════════════════════════════════════ */
  function initCharts() {
    if (metrics.monthly_revenue && metrics.monthly_revenue.length > 0) {
      chartInstances.monthly = buildMonthlyChart('monthlyChart', metrics.monthly_revenue, 'bar');
    }
    if (metrics.daily_revenue && metrics.daily_revenue.length > 0) {
      chartInstances.daily = buildDailyChart('dailyChart', metrics.daily_revenue);
    }
    if (metrics.top_products && metrics.top_products.length > 0) {
      chartInstances.products = buildProductsChart('productsChart', metrics.top_products);
    }
    if (metrics.top_cities && metrics.top_cities.length > 0) {
      chartInstances.cities = buildCitiesChart('citiesChart', metrics.top_cities);
    }
  }

  /* ── Chart type toggle (Bar ↔ Line) ───────────── */
  document.querySelectorAll('.btn-chart-type').forEach(btn => {
    btn.addEventListener('click', function () {
      const canvasId = this.dataset.chart;
      const newType  = this.dataset.type;

      /* Update active state */
      const group = document.querySelectorAll(`[data-chart="${canvasId}"]`);
      group.forEach(b => b.classList.remove('active'));
      this.classList.add('active');

      /* Rebuild chart */
      const old = chartInstances[canvasId.replace('Chart', '')];
      if (old) old.destroy();
      if (canvasId === 'monthlyChart' && metrics.monthly_revenue) {
        chartInstances.monthly = buildMonthlyChart(canvasId, metrics.monthly_revenue, newType);
      }
    });
  });

  /* ════════════════════════════════════════════════
     GST TOGGLE
  ════════════════════════════════════════════════ */
  const gstToggle      = document.getElementById('gstToggle');
  const gstRateSection = document.getElementById('gstRateSection');
  const gstRate        = document.getElementById('gstRate');
  const gstInfo        = document.getElementById('gstInfo');
  const kpiRevenue     = document.getElementById('kpiRevenue');

  if (gstToggle) {
    gstToggle.addEventListener('change', async () => {
      gstRateSection.style.display = gstToggle.checked ? '' : 'none';
      await applyGST();
    });
    if (gstRate) gstRate.addEventListener('change', applyGST);
  }

  async function applyGST() {
    try {
      const res  = await fetch('/api/gst', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({
          dashboard_id: dashId,
          include_gst:  gstToggle ? gstToggle.checked : false,
          gst_rate:     gstRate   ? parseFloat(gstRate.value) : 18,
        }),
      });
      const data = await res.json();
      if (data.success) {
        if (kpiRevenue) kpiRevenue.textContent = data.net_revenue_fmt;
        if (gstInfo) {
          gstInfo.textContent = gstToggle && gstToggle.checked
            ? `Net: ${data.net_revenue_fmt} | GST: ${data.gst_amount_fmt || ''}`
            : '';
        }
      }
    } catch (e) {
      console.error('GST toggle error', e);
    }
  }

  /* ════════════════════════════════════════════════
     SHARE BUTTON
  ════════════════════════════════════════════════ */
  const btnShare = document.getElementById('btnShare');
  if (btnShare) {
    btnShare.addEventListener('click', async () => {
      try {
        const res  = await fetch(`/api/share/${dashId}`);
        const data = await res.json();
        if (data.share_url) {
          const ok = await copyToClipboard(data.share_url);
          showToast(ok ? '🔗 Link copied to clipboard!' : data.share_url, ok ? 'success' : 'info');
        }
      } catch (e) {
        showToast('Could not get share link.', 'error');
      }
    });
  }

  /* ════════════════════════════════════════════════
     WHATSAPP DIGEST MODAL
  ════════════════════════════════════════════════ */
  const btnWhatsApp    = document.getElementById('btnWhatsApp');
  const whatsappModal  = document.getElementById('whatsappModal');
  const modalClose     = document.getElementById('modalClose');
  const modalSend      = document.getElementById('modalSend');
  const whatsappPhone  = document.getElementById('whatsappPhone');
  const whatsappResult = document.getElementById('whatsappResult');

  if (btnWhatsApp) btnWhatsApp.addEventListener('click', () => {
    whatsappModal.style.display = 'flex';
    if (whatsappPhone) whatsappPhone.focus();
  });

  if (modalClose) modalClose.addEventListener('click', () => {
    whatsappModal.style.display = 'none';
    if (whatsappResult) whatsappResult.textContent = '';
  });

  /* Close on backdrop click */
  if (whatsappModal) whatsappModal.addEventListener('click', e => {
    if (e.target === whatsappModal) {
      whatsappModal.style.display = 'none';
    }
  });

  if (modalSend) {
    modalSend.addEventListener('click', async () => {
      const phone = whatsappPhone ? whatsappPhone.value.trim() : '';
      if (!phone) {
        showToast('Please enter your mobile number.', 'error');
        return;
      }
      modalSend.disabled = true;
      modalSend.textContent = 'Sending…';
      if (whatsappResult) whatsappResult.textContent = '';

      try {
        const res  = await fetch('/api/send-digest', {
          method:  'POST',
          headers: { 'Content-Type': 'application/json' },
          body:    JSON.stringify({ dashboard_id: dashId, phone }),
        });
        const data = await res.json();
        if (res.ok && data.success) {
          if (whatsappResult) {
            whatsappResult.textContent = '✅ ' + data.message;
            whatsappResult.style.color = '#22c55e';
          }
          showToast('WhatsApp digest sent! 📲', 'success');
          setTimeout(() => { whatsappModal.style.display = 'none'; }, 2000);
        } else {
          if (whatsappResult) {
            whatsappResult.textContent = '❌ ' + (data.error || 'Send failed.');
            whatsappResult.style.color = '#ef4444';
          }
        }
      } catch (e) {
        if (whatsappResult) {
          whatsappResult.textContent = '❌ Network error.';
          whatsappResult.style.color = '#ef4444';
        }
      } finally {
        modalSend.disabled = false;
        modalSend.textContent = 'Send Digest';
      }
    });
  }

  /* ════════════════════════════════════════════════
     NATURAL LANGUAGE CHAT
  ════════════════════════════════════════════════ */
  const chatInput    = document.getElementById('chatInput');
  const chatSend     = document.getElementById('chatSend');
  const chatMessages = document.getElementById('chatMessages');

  function addMessage(text, role) {
    if (!chatMessages) return;
    const div = document.createElement('div');
    div.className = `chat-msg ${role}`;
    div.textContent = text;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  async function sendChat() {
    if (!chatInput) return;
    const msg = chatInput.value.trim();
    if (!msg) return;

    addMessage(msg, 'user');
    chatInput.value = '';
    chatSend.disabled = true;

    try {
      const res  = await fetch('/api/chat', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ dashboard_id: dashId, message: msg }),
      });
      const data = await res.json();
      const reply = data.message || 'Done! ✅';
      addMessage(reply, 'bot');

      /* Handle chart update actions */
      if (data.action && data.action !== 'answer') {
        handleChatAction(data);
      }
    } catch (e) {
      addMessage('Sorry, something went wrong. Please try again.', 'bot');
    } finally {
      chatSend.disabled = false;
      if (chatInput) chatInput.focus();
    }
  }

  if (chatSend) chatSend.addEventListener('click', sendChat);
  if (chatInput) {
    chatInput.addEventListener('keydown', e => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendChat();
      }
    });
  }

  /* ── Handle AI actions ────────────────────────── */
  function handleChatAction(data) {
    const { action, chart_type, chart_id } = data;

    if (action === 'update_chart' && chart_id === 'monthlyChart' && metrics.monthly_revenue) {
      const type = chart_type || 'bar';
      if (chartInstances.monthly) chartInstances.monthly.destroy();
      chartInstances.monthly = buildMonthlyChart('monthlyChart', metrics.monthly_revenue, type);
      showToast(`Chart updated to ${type}`, 'success');
    }
  }

  /* ════════════════════════════════════════════════
     BOOT
  ════════════════════════════════════════════════ */
  initCharts();

})();
