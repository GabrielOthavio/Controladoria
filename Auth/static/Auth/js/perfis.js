(function () {
  'use strict';

  /* ===== Segmented control ===== */
  var LEVELS = {
    none:  { ver: '',   criar: '',   editar: '',   excluir: '' },
    ver:   { ver: 'on', criar: '',   editar: '',   excluir: '' },
    gerir: { ver: 'on', criar: 'on', editar: 'on', excluir: '' },
    total: { ver: 'on', criar: 'on', editar: 'on', excluir: 'on' },
  };

  function detectLevel(ver, criar, editar, excluir) {
    if (ver && criar && editar && excluir) return 'total';
    if (ver && criar && editar)            return 'gerir';
    if (ver)                               return 'ver';
    return 'none';
  }

  function applyLevel(ctrl, level) {
    var row  = ctrl.dataset.row;
    var vals = LEVELS[level] || LEVELS.none;

    var hVer     = document.querySelector('.h-ver[data-row="'     + row + '"]');
    var hCriar   = document.querySelector('.h-criar[data-row="'   + row + '"]');
    var hEditar  = document.querySelector('.h-editar[data-row="'  + row + '"]');
    var hExcluir = document.querySelector('.h-excluir[data-row="' + row + '"]');
    if (hVer)     hVer.value     = vals.ver;
    if (hCriar)   hCriar.value   = vals.criar;
    if (hEditar)  hEditar.value  = vals.editar;
    if (hExcluir) hExcluir.value = vals.excluir;

    ctrl.querySelectorAll('.seg-btn').forEach(function (btn) {
      var active = btn.dataset.level === level;
      btn.setAttribute('aria-checked', active ? 'true' : 'false');
      btn.tabIndex = active ? 0 : -1;
    });

    markDirty();
  }

  function initSegControls() {
    document.querySelectorAll('.seg-ctrl').forEach(function (ctrl) {
      var level = detectLevel(
        ctrl.dataset.initVer    === '1',
        ctrl.dataset.initCriar  === '1',
        ctrl.dataset.initEditar === '1',
        ctrl.dataset.initExcluir === '1'
      );
      applyLevel(ctrl, level);

      ctrl.querySelectorAll('.seg-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
          applyLevel(ctrl, btn.dataset.level);
        });

        btn.addEventListener('keydown', function (e) {
          var btns = Array.from(ctrl.querySelectorAll('.seg-btn'));
          var idx  = btns.indexOf(btn);
          if (e.key === 'ArrowRight' && idx < btns.length - 1) {
            e.preventDefault();
            btns[idx + 1].focus();
            applyLevel(ctrl, btns[idx + 1].dataset.level);
          }
          if (e.key === 'ArrowLeft' && idx > 0) {
            e.preventDefault();
            btns[idx - 1].focus();
            applyLevel(ctrl, btns[idx - 1].dataset.level);
          }
        });
      });
    });
  }

  /* ===== Presets com toast de undo ===== */
  var undoSnapshot = null;

  function snapshotLevels() {
    var snap = {};
    document.querySelectorAll('.seg-ctrl').forEach(function (ctrl) {
      ctrl.querySelectorAll('.seg-btn').forEach(function (btn) {
        if (btn.getAttribute('aria-checked') === 'true') {
          snap[ctrl.dataset.row] = btn.dataset.level;
        }
      });
    });
    return snap;
  }

  function restoreSnapshot(snap) {
    document.querySelectorAll('.seg-ctrl').forEach(function (ctrl) {
      var level = snap[ctrl.dataset.row];
      if (level) applyLevel(ctrl, level);
    });
  }

  var LEVEL_LABELS = { none: 'Sem acesso', ver: 'Ver', gerir: 'Gerir', total: 'Total' };

  function applyPreset(level) {
    undoSnapshot = snapshotLevels();
    document.querySelectorAll('.seg-ctrl').forEach(function (ctrl) {
      applyLevel(ctrl, level);
    });
    showUndoToast('Preset "' + (LEVEL_LABELS[level] || level) + '" aplicado a todos os módulos.');
  }

  function showUndoToast(message) {
    var stack = document.getElementById('toast-stack');
    if (!stack) return;

    var remaining = 3;
    var toast = document.createElement('div');
    toast.className = 'toast toast-warning';
    toast.setAttribute('role', 'status');

    function render() {
      toast.innerHTML =
        '<i class="bi bi-exclamation-triangle-fill toast-icon"></i>' +
        '<div class="toast-body">' + message +
        ' <button class="undo-btn" style="font-size:11px;text-decoration:underline;background:none;border:none;cursor:pointer;color:inherit;padding:0;font-family:inherit">' +
        'Desfazer (' + remaining + 's)</button></div>' +
        '<button class="toast-close" aria-label="Fechar"><i class="bi bi-x"></i></button>';

      toast.querySelector('.undo-btn').addEventListener('click', function () {
        clearInterval(tick);
        restoreSnapshot(undoSnapshot);
        dismissEl(toast);
      });
      toast.querySelector('.toast-close').addEventListener('click', function () {
        clearInterval(tick);
        dismissEl(toast);
      });
    }

    render();
    stack.appendChild(toast);

    var tick = setInterval(function () {
      remaining--;
      if (remaining <= 0) {
        clearInterval(tick);
        dismissEl(toast);
        return;
      }
      var btn = toast.querySelector('.undo-btn');
      if (btn) btn.textContent = 'Desfazer (' + remaining + 's)';
    }, 1000);
  }

  function dismissEl(el) {
    if (!el.parentNode) return;
    el.classList.add('removing');
    el.addEventListener('animationend', function () { el.remove(); }, { once: true });
  }

  function initPresets() {
    document.querySelectorAll('[data-preset]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        applyPreset(btn.dataset.preset);
      });
    });
  }

  /* ===== Dirty badge ===== */
  var initialState = null;
  var isDirty = false;

  function snapshotForm() {
    var state = {};
    document.querySelectorAll('.h-ver,.h-criar,.h-editar,.h-excluir').forEach(function (inp) {
      state[inp.name] = inp.value;
    });
    var nome = document.querySelector('[name="nome"]');
    var desc = document.querySelector('[name="descricao"]');
    if (nome) state._nome = nome.value;
    if (desc) state._desc = desc.value;
    return JSON.stringify(state);
  }

  function markDirty() {
    if (isDirty) return;
    isDirty = true;
    var badge = document.getElementById('dirty-badge');
    if (badge) badge.hidden = false;
  }

  function checkDirty() {
    if (!initialState) return;
    if (snapshotForm() !== initialState) markDirty();
  }

  function initDirtyBadge() {
    var form = document.getElementById('perfil-form');
    if (!form) return;
    /* snapshot após os seg controls serem inicializados */
    setTimeout(function () { initialState = snapshotForm(); }, 0);
    form.addEventListener('input', checkDirty);
    form.addEventListener('change', checkDirty);
  }

  /* ===== Tree-select (seletor de perfil pai) ===== */
  function initParentSelect() {
    var trigger = document.getElementById('parent-select-trigger');
    var popover = document.getElementById('parent-popover');
    var hidden  = document.getElementById('parent-hidden-input');
    if (!trigger || !popover || !hidden) return;

    function openPop() {
      popover.classList.add('open');
      trigger.setAttribute('aria-expanded', 'true');
      var sel = popover.querySelector('.parent-item.selected');
      if (sel) sel.scrollIntoView({ block: 'nearest' });
    }
    function closePop() {
      popover.classList.remove('open');
      trigger.setAttribute('aria-expanded', 'false');
    }

    trigger.addEventListener('click', function (e) {
      e.stopPropagation();
      popover.classList.contains('open') ? closePop() : openPop();
    });
    document.addEventListener('click', closePop);
    popover.addEventListener('click', function (e) { e.stopPropagation(); });

    popover.querySelectorAll('.parent-item').forEach(function (item) {
      item.addEventListener('click', function () {
        var val   = item.dataset.value || '';
        var label = item.dataset.label;
        hidden.value = val;
        var labelEl = trigger.querySelector('.parent-select-label');
        labelEl.textContent = label;
        labelEl.classList.toggle('placeholder', !val);
        popover.querySelectorAll('.parent-item').forEach(function (x) { x.classList.remove('selected'); });
        item.classList.add('selected');
        closePop();
        markDirty();
      });
    });

    /* Teclado */
    trigger.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ' || e.key === 'ArrowDown') {
        e.preventDefault();
        openPop();
        var first = popover.querySelector('.parent-item');
        if (first) first.focus();
      }
      if (e.key === 'Escape') closePop();
    });

    popover.addEventListener('keydown', function (e) {
      var items = Array.from(popover.querySelectorAll('.parent-item'));
      var idx   = items.indexOf(document.activeElement);
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        items[Math.min(idx + 1, items.length - 1)].focus();
      }
      if (e.key === 'ArrowUp') {
        e.preventDefault();
        if (idx <= 0) { closePop(); trigger.focus(); } else items[idx - 1].focus();
      }
      if (e.key === 'Escape')  { e.preventDefault(); closePop(); trigger.focus(); }
      if (e.key === 'Enter' && idx >= 0) { e.preventDefault(); items[idx].click(); trigger.focus(); }
    });
  }

  /* ===== Árvore — colapsar/expandir (lista.html) ===== */
  function initTreeList() {
    var childrenOf = {};
    document.querySelectorAll('.tree-row[data-parent]').forEach(function (row) {
      var pid = row.dataset.parent;
      if (!childrenOf[pid]) childrenOf[pid] = [];
      childrenOf[pid].push(row.dataset.id);
    });

    /* Torna o toggle visível apenas para nós com filhos */
    Object.keys(childrenOf).forEach(function (pid) {
      var row = document.querySelector('.tree-row[data-id="' + pid + '"]');
      if (row) {
        var btn = row.querySelector('.tree-toggle');
        if (btn) {
          btn.removeAttribute('aria-hidden');
          btn.setAttribute('aria-expanded', 'true');
        }
      }
    });

    function getDescendants(id) {
      var result = [], queue = (childrenOf[id] || []).slice();
      while (queue.length) {
        var cid = queue.shift();
        result.push(cid);
        (childrenOf[cid] || []).forEach(function (x) { queue.push(x); });
      }
      return result;
    }

    function toggleSubtree(id, show) {
      getDescendants(id).forEach(function (cid) {
        var el = document.querySelector('.tree-row[data-id="' + cid + '"]');
        if (el) el.hidden = !show;
      });
    }

    document.querySelectorAll('.tree-toggle').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var row = btn.closest('.tree-row');
        if (!row) return;
        var id        = row.dataset.id;
        var expanded  = btn.getAttribute('aria-expanded') !== 'false';
        var showNext  = !expanded;
        toggleSubtree(id, showNext);
        btn.setAttribute('aria-expanded', showNext ? 'true' : 'false');
        var icon = btn.querySelector('i');
        if (icon) icon.className = showNext ? 'bi bi-chevron-down' : 'bi bi-chevron-right';
      });
    });
  }

  /* ===== Legenda popover ===== */
  function initLegendPopover() {
    document.querySelectorAll('.legend-btn').forEach(function (btn) {
      var wrap    = btn.closest('.legend-wrap');
      var popover = wrap && wrap.querySelector('.legend-popover');
      if (!popover) return;
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        popover.classList.toggle('open');
      });
      document.addEventListener('click', function () { popover.classList.remove('open'); });
      popover.addEventListener('click', function (e) { e.stopPropagation(); });
    });
  }

  /* ===== Init ===== */
  document.addEventListener('DOMContentLoaded', function () {
    initSegControls();
    initPresets();
    initDirtyBadge();
    initParentSelect();
    initTreeList();
    initLegendPopover();
  });
})();
