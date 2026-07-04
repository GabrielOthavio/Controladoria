(function () {
  'use strict';

  /* ===== Tweaks ===== */
  function getTweaks() {
    try { return JSON.parse(localStorage.getItem('app_tweaks') || '{}'); } catch { return {}; }
  }
  function saveTweaks(t) {
    localStorage.setItem('app_tweaks', JSON.stringify(t));
  }
  function applyTweaks(t) {
    document.documentElement.setAttribute('data-theme',   t.theme   || 'dark');
    document.documentElement.setAttribute('data-density', t.density || 'compact');
    if (t.accentH) document.documentElement.style.setProperty('--accent-h', t.accentH);
    if (t.accentC) document.documentElement.style.setProperty('--accent-c', t.accentC);
    if (t.accentL) document.documentElement.style.setProperty('--accent-l', t.accentL);
  }

  /* ===== Sidebar ===== */
  function initSidebar() {
    var sidebar = document.getElementById('sidebar');
    var btn     = document.getElementById('sidebar-toggle');
    var icon    = document.getElementById('sidebar-toggle-icon');
    if (!sidebar || !btn) return;

    var t = getTweaks();
    if (t.sidebarCollapsed) {
      sidebar.classList.add('collapsed');
      if (icon) icon.className = 'bi bi-arrow-bar-right';
    }

    btn.addEventListener('click', function () {
      var collapsed = sidebar.classList.toggle('collapsed');
      var curr = getTweaks();
      curr.sidebarCollapsed = collapsed;
      saveTweaks(curr);
      if (icon) icon.className = collapsed ? 'bi bi-arrow-bar-right' : 'bi bi-arrow-bar-left';
    });
  }

  /* ===== Active nav ===== */
  function initActiveNav() {
    var path = location.pathname;
    document.querySelectorAll('[data-nav-path]').forEach(function (el) {
      var navPath = el.dataset.navPath;
      var exact   = el.dataset.navExact;
      if (!navPath) return;
      var active = exact
        ? path === navPath
        : navPath.length > 1 && path.startsWith(navPath);
      if (active) el.classList.add('active');
    });
  }

  /* ===== Tweaks panel ===== */
  function initTweaks() {
    var btn      = document.getElementById('tweaks-btn');
    var dropdown = document.getElementById('tweaks-dropdown');
    if (!btn || !dropdown) return;

    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      dropdown.classList.toggle('open');
    });
    document.addEventListener('click', function () {
      dropdown.classList.remove('open');
    });
    dropdown.addEventListener('click', function (e) { e.stopPropagation(); });

    var t = getTweaks();

    /* Theme */
    dropdown.querySelectorAll('[data-theme-opt]').forEach(function (el) {
      if (el.dataset.themeOpt === (t.theme || 'dark')) el.classList.add('active');
      el.addEventListener('click', function () {
        dropdown.querySelectorAll('[data-theme-opt]').forEach(function (x) { x.classList.remove('active'); });
        el.classList.add('active');
        var curr = getTweaks(); curr.theme = el.dataset.themeOpt;
        saveTweaks(curr); applyTweaks(curr);
      });
    });

    /* Density */
    dropdown.querySelectorAll('[data-density-opt]').forEach(function (el) {
      if (el.dataset.densityOpt === (t.density || 'compact')) el.classList.add('active');
      el.addEventListener('click', function () {
        dropdown.querySelectorAll('[data-density-opt]').forEach(function (x) { x.classList.remove('active'); });
        el.classList.add('active');
        var curr = getTweaks(); curr.density = el.dataset.densityOpt;
        saveTweaks(curr); applyTweaks(curr);
      });
    });
  }

  /* ===== Toast ===== */
  var TOAST_ICONS = {
    success: 'bi-check-circle-fill',
    error:   'bi-x-circle-fill',
    warning: 'bi-exclamation-triangle-fill',
    info:    'bi-info-circle-fill',
  };

  function showToast(message, type, opts) {
    var stack = document.getElementById('toast-stack');
    if (!stack) return;
    type = type || 'info';
    opts = opts || {};
    var icon = TOAST_ICONS[type] || TOAST_ICONS.info;
    var toast = document.createElement('div');
    toast.className = 'toast toast-' + type;

    var iconEl = document.createElement('i');
    iconEl.className = 'bi ' + icon + ' toast-icon';

    var bodyEl = document.createElement('div');
    bodyEl.className = 'toast-body';
    if (opts.raw) {
      bodyEl.innerHTML = message;
    } else {
      bodyEl.textContent = message;
    }

    var closeBtn = document.createElement('button');
    closeBtn.className = 'toast-close';
    closeBtn.setAttribute('aria-label', 'Fechar');
    var closeIcon = document.createElement('i');
    closeIcon.className = 'bi bi-x';
    closeBtn.appendChild(closeIcon);
    closeBtn.addEventListener('click', function () {
      dismissToast(toast);
    });

    toast.appendChild(iconEl);
    toast.appendChild(bodyEl);
    toast.appendChild(closeBtn);
    stack.appendChild(toast);
    toast._timer = setTimeout(function () { dismissToast(toast); }, 4500);
  }

  function dismissToast(toast) {
    if (!toast.parentNode) return;
    clearTimeout(toast._timer);
    toast.classList.add('removing');
    toast.addEventListener('animationend', function () { toast.remove(); }, { once: true });
  }

  /* Convert hidden Django message spans → toasts */
  function initMessages() {
    document.querySelectorAll('[data-django-message]').forEach(function (el) {
      var tags = el.dataset.djangoMessage || '';
      var type = 'info';
      if (tags.includes('success')) type = 'success';
      else if (tags.includes('error') || tags.includes('danger')) type = 'error';
      else if (tags.includes('warning')) type = 'warning';
      showToast(el.textContent.trim(), type);
      el.remove();
    });
  }

  /* ===== Keyboard shortcuts ===== */
  function initShortcuts() {
    var gPressed = false, gTimer;

    document.addEventListener('keydown', function (e) {
      var active = document.activeElement || {};
      var tag = active.tagName;
      var editing = tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' ||
        active.isContentEditable;

      /* Esc — close tweaks */
      if (e.key === 'Escape') {
        var dd = document.getElementById('tweaks-dropdown');
        if (dd) dd.classList.remove('open');
        return;
      }

      if (editing) return;

      /* / — focus search (future) */
      if (e.key === '/') {
        e.preventDefault();
        var search = document.querySelector('[data-search-input]');
        if (search) search.focus();
        return;
      }

      /* N — new record */
      if (e.key === 'n' || e.key === 'N') {
        var newBtn = document.querySelector('[data-shortcut-new]');
        if (newBtn) { e.preventDefault(); newBtn.click(); }
        return;
      }

      /* ? — show shortcut hints */
      if (e.key === '?') {
        e.preventDefault();
        showToast(
          '<strong>Atalhos:</strong> N = novo registro &nbsp;·&nbsp; G+D = dashboard &nbsp;·&nbsp; G+A = ações &nbsp;·&nbsp; G+U = auditorias &nbsp;·&nbsp; G+I = índices',
          'info',
          { raw: true }
        );
        return;
      }

      /* G+D, G+A, G+U, G+I — navegação */
      if (e.key === 'g' || e.key === 'G') {
        gPressed = true;
        clearTimeout(gTimer);
        gTimer = setTimeout(function () { gPressed = false; }, 1200);
        return;
      }
      if (gPressed) {
        clearTimeout(gTimer);
        gPressed = false;
        if (e.key === 'd' || e.key === 'D') {
          var dashLink = document.querySelector('[data-nav-path][data-nav-exact]');
          if (dashLink) location.href = dashLink.href;
        }
        if (e.key === 'a' || e.key === 'A') {
          var acoesLink = document.querySelector('[data-nav-key="acoes"]');
          if (acoesLink) location.href = acoesLink.href;
        }
        if (e.key === 'u' || e.key === 'U') {
          var audLink = document.querySelector('[data-nav-key="auditorias"]');
          if (audLink) location.href = audLink.href;
        }
        if (e.key === 'i' || e.key === 'I') {
          var idxLink = document.querySelector('[data-nav-key="indices"]');
          if (idxLink) location.href = idxLink.href;
        }
      }
    });
  }

  /* ===== Confirmação de ações destrutivas (Etnometodologia — ação incorreta retorna ao estado anterior) ===== */
  function initConfirm() {
    document.querySelectorAll('[data-confirm]').forEach(function (el) {
      el.addEventListener('click', function (e) {
        if (!window.confirm(el.dataset.confirm)) {
          e.preventDefault();
        }
      });
    });
  }

  /* ===== Pagination controls (shared across all list pages) ===== */
  function initPagination() {
    /* Page input — navigate on Enter or blur */
    document.querySelectorAll('.pg-input').forEach(function (inp) {
      var max = parseInt(inp.dataset.max, 10) || 1;

      function goTo() {
        var p = parseInt(inp.value, 10);
        if (isNaN(p) || p < 1) p = 1;
        if (p > max) p = max;
        var url = new URL(window.location.href);
        url.searchParams.set('page', p);
        window.location.href = url.toString();
      }

      inp.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') { e.preventDefault(); goTo(); }
        if (e.key === 'Escape') { inp.value = inp.defaultValue; inp.blur(); }
      });
      inp.addEventListener('blur', function () {
        var p = parseInt(inp.value, 10);
        if (!isNaN(p) && p >= 1 && p <= max) goTo();
        else inp.value = inp.defaultValue;
      });
      inp.addEventListener('focus', function () { this.select(); });
    });

    /* Per-page select */
    document.querySelectorAll('.pg-per-page').forEach(function (sel) {
      sel.addEventListener('change', function () {
        var url = new URL(window.location.href);
        url.searchParams.set('per_page', this.value);
        url.searchParams.set('page', '1');
        window.location.href = url.toString();
      });
    });
  }

  /* ===== Avatar dropdown ===== */
  function initAvatarMenu() {
    var menu     = document.getElementById('user-menu');
    var btn      = document.getElementById('user-menu-btn');
    var dropdown = document.getElementById('user-dropdown');
    if (!menu || !btn || !dropdown) return;

    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = dropdown.classList.toggle('open');
      btn.classList.toggle('open', open);
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('click', function () {
      dropdown.classList.remove('open');
      btn.classList.remove('open');
      btn.setAttribute('aria-expanded', 'false');
    });
    dropdown.addEventListener('click', function (e) { e.stopPropagation(); });

    menu.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        dropdown.classList.remove('open');
        btn.classList.remove('open');
        btn.setAttribute('aria-expanded', 'false');
        btn.focus();
      }
    });
  }

  /* ===== Init ===== */
  document.addEventListener('DOMContentLoaded', function () {
    initSidebar();
    initActiveNav();
    initTweaks();
    initMessages();
    initShortcuts();
    initConfirm();
    initPagination();
    initAvatarMenu();
  });

  window.showToast = showToast;
})();
