function TweaksToggle({ tweaks, setTweaks }) {
  const [open, setOpen] = React.useState(false);

  const setTheme = (theme) => {
    document.body.setAttribute('data-theme', theme);
    setTweaks(t => ({ ...t, theme }));
  };

  const setDensity = (density) => {
    document.body.setAttribute('data-density', density);
    setTweaks(t => ({ ...t, density }));
  };

  const ACCENTS = [
    { name: 'indigo', h: 265 }, { name: 'blue',   h: 220 },
    { name: 'violet', h: 280 }, { name: 'rose',    h: 350 },
    { name: 'amber',  h: 45  }, { name: 'teal',    h: 175 },
  ];

  const setAccent = (accent) => {
    const found = ACCENTS.find(a => a.name === accent);
    if (found) document.documentElement.style.setProperty('--accent-h', found.h);
    setTweaks(t => ({ ...t, accent }));
  };

  return (
    <div style={{ position: 'relative' }}>
      <button className="btn btn-ghost btn-icon" onClick={() => setOpen(o => !o)} title="Aparência">
        <i className="bi bi-palette" />
      </button>

      {open && (
        <>
          <div
            style={{ position: 'fixed', inset: 0, zIndex: 99 }}
            onClick={() => setOpen(false)}
          />
          <div style={{
            position: 'absolute', right: 0, top: 36, zIndex: 100, width: 240,
            background: 'var(--bg-elev)', border: '1px solid var(--border)',
            borderRadius: 'var(--radius-lg)', boxShadow: 'var(--shadow-lg)',
            overflow: 'hidden',
          }}>
            <div style={{ padding: '10px 14px', borderBottom: '1px solid var(--border)', fontWeight: 600, fontSize: 13 }}>
              Aparência
            </div>
            <div style={{ padding: '12px 14px', display: 'flex', flexDirection: 'column', gap: 14 }}>

              {/* Theme */}
              <div>
                <div style={{ fontSize: 11, fontWeight: 500, color: 'var(--fg-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 6 }}>Tema</div>
                <div style={{ display: 'flex', background: 'var(--bg-sunken)', border: '1px solid var(--border)', borderRadius: 6, padding: 2, gap: 2 }}>
                  {['light', 'dark'].map(t => (
                    <button
                      key={t}
                      onClick={() => setTheme(t)}
                      style={{
                        flex: 1, border: 0, borderRadius: 4, padding: '5px 8px',
                        fontFamily: 'inherit', fontSize: 12, cursor: 'pointer',
                        background: tweaks.theme === t ? 'var(--bg-elev)' : 'transparent',
                        color: tweaks.theme === t ? 'var(--fg)' : 'var(--fg-muted)',
                        fontWeight: tweaks.theme === t ? 600 : 400,
                        boxShadow: tweaks.theme === t ? 'var(--shadow-sm)' : 'none',
                      }}
                    >
                      {t === 'light' ? 'Claro' : 'Escuro'}
                    </button>
                  ))}
                </div>
              </div>

              {/* Density */}
              <div>
                <div style={{ fontSize: 11, fontWeight: 500, color: 'var(--fg-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 6 }}>Densidade</div>
                <div style={{ display: 'flex', background: 'var(--bg-sunken)', border: '1px solid var(--border)', borderRadius: 6, padding: 2, gap: 2 }}>
                  {[['compact', 'Compacto'], ['comfortable', 'Normal'], ['spacious', 'Espaçoso']].map(([d, lbl]) => (
                    <button
                      key={d}
                      onClick={() => setDensity(d)}
                      style={{
                        flex: 1, border: 0, borderRadius: 4, padding: '5px 4px',
                        fontFamily: 'inherit', fontSize: 11, cursor: 'pointer',
                        background: tweaks.density === d ? 'var(--bg-elev)' : 'transparent',
                        color: tweaks.density === d ? 'var(--fg)' : 'var(--fg-muted)',
                        fontWeight: tweaks.density === d ? 600 : 400,
                        boxShadow: tweaks.density === d ? 'var(--shadow-sm)' : 'none',
                      }}
                    >
                      {lbl}
                    </button>
                  ))}
                </div>
              </div>

              {/* Accent color */}
              <div>
                <div style={{ fontSize: 11, fontWeight: 500, color: 'var(--fg-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 8 }}>Cor de Destaque</div>
                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                  {ACCENTS.map(a => (
                    <div
                      key={a.name}
                      onClick={() => setAccent(a.name)}
                      title={a.name}
                      style={{
                        width: 24, height: 24, borderRadius: '50%', cursor: 'pointer',
                        background: `oklch(0.55 0.15 ${a.h})`,
                        border: `2px solid ${tweaks.accent === a.name ? 'var(--fg)' : 'transparent'}`,
                        transition: 'border-color 0.15s',
                      }}
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
