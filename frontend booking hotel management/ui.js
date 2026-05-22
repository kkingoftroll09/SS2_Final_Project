/**
 * UI Utilities — Toast, Modal, Confirm, Validation helpers
 */

// ── Toast ──────────────────────────────────────────────────────────────────
const Toast = (() => {
  let container;

  function init() {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  function show(message, type = 'info', duration = 3500) {
    const icons = { success: '✓', error: '✕', info: 'i' };
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span class="toast-icon" style="font-weight:700;font-size:0.8rem">${icons[type] || icons.info}</span><span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(6px)';
      toast.style.transition = 'all 0.25s';
      setTimeout(() => toast.remove(), 250);
    }, duration);
  }

  return {
    init,
    success: (msg) => show(msg, 'success'),
    error:   (msg) => show(msg, 'error'),
    info:    (msg) => show(msg, 'info'),
  };
})();

// ── Modal ──────────────────────────────────────────────────────────────────
const Modal = (() => {
  function create(title, bodyHTML, footerHTML = '') {
    const backdrop = document.createElement('div');
    backdrop.className = 'modal-backdrop';
    backdrop.innerHTML = `
      <div class="modal">
        <div class="modal-header">
          <span class="modal-title">${title}</span>
          <button class="modal-close" aria-label="Close">&times;</button>
        </div>
        <div class="modal-body">${bodyHTML}</div>
        ${footerHTML ? `<div class="modal-footer">${footerHTML}</div>` : ''}
      </div>`;

    document.body.appendChild(backdrop);
    requestAnimationFrame(() => backdrop.classList.add('open'));

    const closeModal = () => {
      backdrop.classList.remove('open');
      setTimeout(() => backdrop.remove(), 200);
    };

    backdrop.querySelector('.modal-close').addEventListener('click', closeModal);
    backdrop.addEventListener('click', (e) => { if (e.target === backdrop) closeModal(); });

    return { el: backdrop, close: closeModal };
  }

  return { create };
})();

// ── Confirm ────────────────────────────────────────────────────────────────
function confirmDialog(message, onConfirm) {
  const backdrop = document.createElement('div');
  backdrop.className = 'modal-backdrop';
  backdrop.innerHTML = `
    <div class="confirm-dialog">
      <div class="confirm-icon">!</div>
      <div class="confirm-title">Are you sure?</div>
      <div class="confirm-text">${message}</div>
      <div class="confirm-actions">
        <button class="btn btn-outline" id="confirm-cancel">Cancel</button>
        <button class="btn btn-danger" id="confirm-ok">Delete</button>
      </div>
    </div>`;

  document.body.appendChild(backdrop);
  requestAnimationFrame(() => backdrop.classList.add('open'));

  const close = () => {
    backdrop.classList.remove('open');
    setTimeout(() => backdrop.remove(), 200);
  };

  backdrop.querySelector('#confirm-cancel').addEventListener('click', close);
  backdrop.querySelector('#confirm-ok').addEventListener('click', () => {
    close();
    onConfirm();
  });
}

// ── Form Validation ────────────────────────────────────────────────────────
const Validate = (() => {
  const rules = {
    required: (v) => (v == null || String(v).trim() === '') ? 'This field is required.' : null,
    email:    (v) => /\S+@\S+\.\S+/.test(v) ? null : 'Enter a valid email address.',
    minLen:   (n) => (v) => String(v).length >= n ? null : `Must be at least ${n} characters.`,
    maxLen:   (n) => (v) => String(v).length <= n ? null : `Must be at most ${n} characters.`,
    phone:    (v) => /^[+\d\s\-().]{7,20}$/.test(v) ? null : 'Enter a valid phone number.',
    positiveNum: (v) => (!isNaN(v) && Number(v) > 0) ? null : 'Must be a positive number.',
    nonNegNum:   (v) => (!isNaN(v) && Number(v) >= 0) ? null : 'Must be 0 or greater.',
    dateNotPast: (v) => {
      const d = new Date(v);
      const today = new Date(); today.setHours(0,0,0,0);
      return d >= today ? null : 'Date cannot be in the past.';
    },
    checkoutAfterCheckin: (checkin) => (checkout) => {
      return new Date(checkout) > new Date(checkin) ? null : 'Check-out must be after check-in.';
    },
  };

  function validateField(input, fieldRules) {
    const errEl = document.getElementById(input.id + '-err');
    const val = input.value;
    for (const rule of fieldRules) {
      const err = rule(val);
      if (err) {
        input.classList.add('error');
        if (errEl) { errEl.textContent = err; errEl.classList.add('visible'); }
        return false;
      }
    }
    input.classList.remove('error');
    if (errEl) errEl.classList.remove('visible');
    return true;
  }

  function validateForm(schema) {
    let valid = true;
    for (const [id, fieldRules] of Object.entries(schema)) {
      const input = document.getElementById(id);
      if (!input) continue;
      if (!validateField(input, fieldRules)) valid = false;
    }
    return valid;
  }

  function attachLiveValidation(schema) {
    for (const [id, fieldRules] of Object.entries(schema)) {
      const input = document.getElementById(id);
      if (!input) continue;
      input.addEventListener('blur', () => validateField(input, fieldRules));
      input.addEventListener('input', () => {
        if (input.classList.contains('error')) validateField(input, fieldRules);
      });
    }
  }

  function getFormData(formEl) {
    const data = {};
    formEl.querySelectorAll('[name]').forEach(el => {
      data[el.name] = el.type === 'number' ? (el.value === '' ? null : Number(el.value)) : el.value || null;
    });
    return data;
  }

  return { rules, validateField, validateForm, attachLiveValidation, getFormData };
})();

// ── Loading state for buttons ─────────────────────────────────────────────
function setLoading(btn, loading) {
  if (loading) {
    btn.dataset.origText = btn.innerHTML;
    btn.innerHTML = '<span class="spinner"></span>';
    btn.disabled = true;
  } else {
    btn.innerHTML = btn.dataset.origText || btn.innerHTML;
    btn.disabled = false;
  }
}

// ── Format helpers ─────────────────────────────────────────────────────────
const fmt = {
  currency: (n) => '$' + Number(n || 0).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ','),
  date:     (d) => d ? new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' }) : '—',
  initials: (name) => name ? name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2) : '?',
  badge:    (status, map) => {
    const cls = map[status?.toLowerCase()] || 'muted';
    return `<span class="badge badge-${cls}">${status || '—'}</span>`;
  },
};

const statusMap = {
  booking: { confirmed: 'success', pending: 'warning', cancelled: 'danger', 'checked-in': 'info', 'checked-out': 'muted' },
  payment: { completed: 'success', pending: 'warning', failed: 'danger', refunded: 'info' },
  room:    { available: 'success', occupied: 'danger', cleaning: 'warning', maintenance: 'info' },
};
