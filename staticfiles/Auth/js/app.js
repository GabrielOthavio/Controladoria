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

  function showToast(message, type) {
    var stack = document.getElementById('toast-stack');
    if (!stack) return;
    type = type || 'info';
    var icon = TOAST_ICONS[type] || TOAST_ICONS.info;
    var toast = document.createElement('div');
    toast.className = 'toast toast-' + type;
    toast.innerHTML =
      '<i class="bi ' + icon + ' toast-icon"></i>' +
      '<div class="toast-body">' + message + '</div>' +
      '<button class="toast-close" aria-label="Fechar"><i class="bi bi-x"></i></button>';
    toast.querySelector('.toast-close').addEventListener('click', function () {
      dismissToast(toast);
    });
    stack.appendChild(toast);
    setTimeout(function () { dismissToast(toast); }, 4500);
  }

  function dismissToast(toast) {
    if (!toast.parentNode) return;
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
      var tag = document.activeElement.tagName;
      var editing = tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' ||
        document.activeElement.isContentEditable;

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

      /* G+D — dashboard, G+A — actions */
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
  });

  window.showToast = showToast;
})();
