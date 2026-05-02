const { useState } = React;

function Shell({ view, setView, tweaks, setTweaks, children }) {
  const [collapsed, setCollapsed] = useState(window.APP_DEFAULTS.sidebarCollapsed);
  const isChefe = window.CURRENT_USER.perfil === 'CHEFE';

  const navGroups = [
    {
      title: 'Principal',
      items: [
        { key: 'dashboard',  icon: 'bi-speedometer2', label: 'Dashboard' },
        { key: 'auditorias', icon: 'bi-clipboard-check', label: 'Auditorias' },
        { key: 'acoes',      icon: 'bi-lightning-charge', label: 'Ações' },
        { key: 'indices',    icon: 'bi-graph-up', label: 'Índices' },
      ],
    },
    {
      title: 'Configuração',
      items: [
        { key: 'tipos_acao',   icon: 'bi-tag',           label: 'Tipos de Ação' },
        { key: 'tipos_indice', icon: 'bi-layers',         label: 'Tipos de Índice' },
        { key: 'grupos',       icon: 'bi-collection',     label: 'Grupos' },
        { key: 'matrizes',   icon: 'bi-journal-check',  label: 'Matrizes de Auditoria' },
        { key: 'entidades',  icon: 'bi-building',        label: 'Entidades' },
        ...(isChefe ? [{ key: 'usuarios', icon: 'bi-people', label: 'Usuários' }] : []),
      ],
    },
  ];

  return (
    <div className="shell">
      {/* Sidebar */}
      <nav className={`sidebar${collapsed ? ' collapsed' : ''}`}>
        <div className="sidebar-head">
          <div className="logo-mark">C</div>
          <span className="logo-text">Controladoria</span>
        </div>

        {navGroups.map(group => (
          <div key={group.title} className="nav-section">
            <div className="nav-section-title">{group.title}</div>
            {group.items.map(item => (
              <button
                key={item.key}
                className={`nav-item${view === item.key ? ' active' : ''}`}
                onClick={() => setView(item.key)}
                title={collapsed ? item.label : undefined}
              >
                <i className={`bi ${item.icon}`} />
                <span className="nav-label">{item.label}</span>
              </button>
            ))}
          </div>
        ))}

        <div className="sidebar-foot">
          <button
            className="nav-item"
            onClick={() => setCollapsed(c => !c)}
            title={collapsed ? 'Expandir' : 'Recolher'}
          >
            <i className={`bi ${collapsed ? 'bi-arrow-bar-right' : 'bi-arrow-bar-left'}`} />
            <span className="nav-label">Recolher</span>
          </button>
        </div>
      </nav>

      {/* Main */}
      <div className="main-col">
        <header className="topbar">
          <div className="breadcrumb" style={{ flex: 1 }}>
            <span>Controladoria</span>
            <span className="current" style={{ color: 'var(--fg-subtle)' }}>/</span>
            <span className="current">{navGroups.flatMap(g => g.items).find(i => i.key === view)?.label ?? view}</span>
          </div>
          <span style={{ fontSize: 12, color: 'var(--fg-muted)' }}>
            {window.CURRENT_USER.fullName || window.CURRENT_USER.username}
          </span>
          <TweaksToggle tweaks={tweaks} setTweaks={setTweaks} />
          <form method="post" action="/logout/" style={{ margin: 0 }}>
            <input type="hidden" name="csrfmiddlewaretoken" value={window.CSRF_TOKEN} />
            <button type="submit" className="btn btn-ghost btn-sm">
              <i className="bi bi-box-arrow-right" /> Sair
            </button>
          </form>
        </header>

        <main className="page">{children}</main>
      </div>
    </div>
  );
}
