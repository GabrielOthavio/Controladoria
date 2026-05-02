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

function App() {
  const [tweaks, setTweaks] = useState({ ...window.APP_DEFAULTS });
  const [view, setView]     = useState('dashboard');

  // Sync tweaks → body attributes on mount
  useEffect(() => {
    document.body.setAttribute('data-theme',   tweaks.theme);
    document.body.setAttribute('data-density', tweaks.density);
  }, []);

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
