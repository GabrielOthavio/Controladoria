const { useState, useEffect } = React;

const DJANGO_REDIRECTS = {
  auditorias:   '/auditorias/',
  acoes:        '/acoes/',
  indices:      '/indices/',
  tipos_acao:   '/tipos-acao/',
  tipos_indice: '/tipos-indice/',
  grupos:       '/grupos-indice/',
  matrizes:     '/matrizes/',
  entidades:    '/entidades/',
  usuarios:     '/usuarios/',
};

function loadTweaks() {
  try {
    var t = JSON.parse(localStorage.getItem('app_tweaks') || '{}');
    return {
      theme:           t.theme           || window.APP_DEFAULTS.theme,
      density:         t.density         || window.APP_DEFAULTS.density,
      accent:          t.accent          || window.APP_DEFAULTS.accent,
      sidebarCollapsed: t.sidebarCollapsed || window.APP_DEFAULTS.sidebarCollapsed,
      accentH:         t.accentH,
    };
  } catch(e) {
    return { ...window.APP_DEFAULTS };
  }
}

function persistTweaks(t) {
  try { localStorage.setItem('app_tweaks', JSON.stringify(t)); } catch(e) {}
  document.documentElement.setAttribute('data-theme',   t.theme   || 'dark');
  document.documentElement.setAttribute('data-density', t.density || 'compact');
  if (t.accentH) document.documentElement.style.setProperty('--accent-h', t.accentH);
}

function App() {
  const [tweaks, setTweaks] = useState(loadTweaks);
  const [view, setView]     = useState('dashboard');

  // Sync tweaks → localStorage + documentElement on every change
  useEffect(() => { persistTweaks(tweaks); }, [tweaks]);

  // Navigate to Django views for pages not yet in React
  const handleSetView = (v) => {
    if (DJANGO_REDIRECTS[v]) {
      window.location.href = DJANGO_REDIRECTS[v];
    } else {
      setView(v);
    }
  };

  const renderView = () => {
    switch (view) {
      case 'dashboard': return <Dashboard />;
      default:          return <Dashboard />;
    }
  };

  return (
    <Shell view={view} setView={handleSetView} tweaks={tweaks} setTweaks={setTweaks}>
      {renderView()}
    </Shell>
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
