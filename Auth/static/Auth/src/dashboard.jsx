const { useState, useEffect } = React;

// ─── Stat Card ────────────────────────────────────────────
function StatCard({ icon, label, value, loading }) {
  return (
    <div className="card">
      <div className="stat">
        <div className="stat-icon"><i className={`bi ${icon}`} /></div>
        <div className="stat-label">{label}</div>
        {loading
          ? <div className="skel" style={{ height: 36, width: 80, marginTop: 4 }} />
          : <div className="stat-value">{value ?? '—'}</div>
        }
      </div>
    </div>
  );
}

// ─── PAINT Pipeline ───────────────────────────────────────
function PAINTPipeline({ statusData, total, loading }) {
  if (loading) {
    return (
      <div className="card" style={{ marginBottom: 20 }}>
        <div className="card-header"><h3 className="card-title">Trilha PAINT</h3></div>
        <div className="card-body">
          <div style={{ display: 'flex', gap: 10 }}>
            {PAINT_STAGES.map(s => (
              <div key={s.key} className="skel paint-stage" style={{ height: 110 }} />
            ))}
          </div>
        </div>
      </div>
    );
  }

  const counts = (statusData || []).reduce((acc, { status, total: n }) => {
    acc[status] = n;
    return acc;
  }, {});

  const concluidas = counts['CONCLUIDA'] || 0;
  const pct = total > 0 ? ((concluidas / total) * 100).toFixed(1) : 0;

  return (
    <div className="card" style={{ marginBottom: 20 }}>
      <div className="card-header">
        <div>
          <h3 className="card-title">Trilha PAINT — Progresso das Auditorias</h3>
          <p className="card-subtitle">{total} auditoria{total !== 1 ? 's' : ''} no total</p>
        </div>
      </div>
      <div className="card-body">
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {PAINT_STAGES.map((stage, i) => (
            <React.Fragment key={stage.key}>
              <div className="paint-stage">
                <div className="paint-letter" style={{ background: stage.color }}>
                  {stage.letter}
                </div>
                <div className="paint-count">{counts[stage.key] || 0}</div>
                <div className="paint-label">{stage.label}</div>
              </div>
              {i < PAINT_STAGES.length - 1 && (
                <i className="bi bi-arrow-right paint-arrow" />
              )}
            </React.Fragment>
          ))}
        </div>

        {total > 0 && (
          <div style={{ marginTop: 14 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, color: 'var(--fg-muted)', marginBottom: 6 }}>
              <span>Taxa de conclusão</span>
              <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{pct}%</span>
            </div>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${pct}%`, background: '#10b981' }}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Change Detail Modal ──────────────────────────────────
function ChangeDetailModal({ entry, onClose }) {
  if (!entry) return null;

  const anterior  = entry.estado_anterior  || {};
  const posterior = entry.estado_posterior || {};
  const HIDDEN_KEYS = new Set(['id']);
  const allKeys   = [...new Set([...Object.keys(anterior), ...Object.keys(posterior)])].filter(k => !HIDDEN_KEYS.has(k));

  function renderValue(val) {
    if (val === null || val === undefined)
      return <span style={{ color: 'var(--fg-subtle)', fontStyle: 'italic' }}>—</span>;
    if (typeof val === 'boolean')
      return <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11 }}>{val ? 'true' : 'false'}</span>;
    if (typeof val === 'object')
      return <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11 }}>{JSON.stringify(val)}</span>;
    return <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11 }}>{String(val)}</span>;
  }

  function isChanged(key) {
    return JSON.stringify(anterior[key]) !== JSON.stringify(posterior[key]);
  }

  const OPERACAO_COLOR = { CRIADO: 'var(--success)', ATUALIZADO: 'var(--warning)', EXCLUIDO: 'var(--danger)' };

  return (
    <div className="confirm-overlay" onClick={onClose}>
      <div
        className="card confirm-dialog"
        style={{ width: 720, maxWidth: '96vw', maxHeight: '88vh', display: 'flex', flexDirection: 'column' }}
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="confirm-header" style={{ gap: 10 }}>
          <i className="bi bi-eye" style={{ fontSize: 18, color: 'var(--accent)' }} />
          <h3 className="confirm-title">Detalhes da Alteração</h3>
          <button
            onClick={onClose}
            style={{ marginLeft: 'auto', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--fg-muted)', fontSize: 16, padding: '2px 6px', borderRadius: 'var(--radius-sm)' }}
          >
            <i className="bi bi-x-lg" />
          </button>
        </div>

        {/* Body */}
        <div style={{ overflowY: 'auto', flex: 1, padding: '16px 20px' }}>
          {/* Meta */}
          <div className="confirm-details" style={{ marginBottom: 16 }}>
            <span><i className="bi bi-tag" /> <strong>{entry.tipo_objeto}</strong></span>
            <span>
              <i className="bi bi-activity" />
              <span style={{ fontWeight: 600, color: OPERACAO_COLOR[entry.operacao] }}>{entry.operacao}</span>
            </span>
            <span><i className="bi bi-person" /> {entry.usuario}</span>
            <span><i className="bi bi-clock" /> {entry.data_hora}</span>
            {entry.uuid_objeto && (
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11 }}>
                <i className="bi bi-fingerprint" /> {entry.uuid_objeto}
              </span>
            )}
          </div>

          {/* Comparison table */}
          {allKeys.length > 0 ? (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th style={{ width: 160 }}>Campo</th>
                    <th>Dado Anterior</th>
                    <th>Dado Posterior</th>
                  </tr>
                </thead>
                <tbody>
                  {allKeys.map(key => (
                    <tr key={key} style={isChanged(key) ? { background: 'oklch(0.5 0.08 75 / 0.08)' } : {}}>
                      <td style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--fg-muted)' }}>
                        {isChanged(key) && <i className="bi bi-pencil-fill" style={{ fontSize: 9, marginRight: 5, color: 'var(--warning)' }} />}
                        {key}
                      </td>
                      <td style={{ color: isChanged(key) ? 'var(--danger)' : 'var(--fg-muted)', maxWidth: 240, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {renderValue(anterior[key])}
                      </td>
                      <td style={{ color: isChanged(key) ? 'var(--success)' : 'var(--fg-muted)', maxWidth: 240, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {renderValue(posterior[key])}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p style={{ color: 'var(--fg-subtle)', fontStyle: 'italic', textAlign: 'center', margin: '24px 0' }}>
              Nenhum detalhe de estado disponível para este registro.
            </p>
          )}
        </div>

        {/* Footer */}
        <div className="confirm-actions">
          <button className="btn btn-secondary" onClick={onClose}>Fechar</button>
        </div>
      </div>
    </div>
  );
}

// ─── Audit Trail ──────────────────────────────────────────
function AuditTrail({ entries, loading }) {
  const [selected, setSelected] = useState(null);

  if (loading) {
    return (
      <div className="card">
        <div className="card-header"><h3 className="card-title">Trilha de Auditoria</h3></div>
        <div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="skel" style={{ height: 20 }} />
          ))}
        </div>
      </div>
    );
  }

  if (!entries || entries.length === 0) {
    return (
      <div className="card">
        <div className="card-header"><h3 className="card-title">Trilha de Auditoria</h3></div>
        <div className="empty">
          <div className="empty-icon"><i className="bi bi-clock-history" /></div>
          <p className="empty-title">Nenhuma alteração registrada</p>
          <p className="empty-msg">Alterações via Signals aparecerão aqui automaticamente.</p>
        </div>
      </div>
    );
  }

  return (
    <>
      {selected && <ChangeDetailModal entry={selected} onClose={() => setSelected(null)} />}
      <div className="card">
        <div className="card-header">
          <div>
            <h3 className="card-title">Trilha de Auditoria</h3>
            <p className="card-subtitle">Últimas {entries.length} alterações capturadas via Django Signals</p>
          </div>
        </div>
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Tipo</th>
                <th>Descrição</th>
                <th>Usuário</th>
                <th className="right">Data / Hora</th>
                <th style={{ width: 40 }}></th>
              </tr>
            </thead>
            <tbody>
              {entries.map(entry => (
                <tr key={entry.id}>
                  <td>
                    <span className="badge">
                      <i className={`bi ${TIPO_ICON[entry.tipo_objeto] || 'bi-file-text'}`} />
                      {entry.tipo_objeto}
                    </span>
                  </td>
                  <td style={{ maxWidth: 320, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', color: 'var(--fg-muted)' }}>
                    <span style={{ fontWeight: 600, marginRight: 6 }}>{entry.operacao}</span>
                    {entry.uuid_objeto && <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11 }}>{entry.uuid_objeto.slice(0, 8)}…</span>}
                  </td>
                  <td style={{ fontSize: 12, color: 'var(--fg-muted)' }}>
                    {entry.usuario === 'Sistema'
                      ? <span style={{ color: 'var(--fg-subtle)', fontStyle: 'italic' }}>Sistema</span>
                      : entry.usuario}
                  </td>
                  <td className="right num" style={{ fontSize: 12, color: 'var(--fg-subtle)', whiteSpace: 'nowrap' }}>
                    {entry.data_hora}
                  </td>
                  <td style={{ textAlign: 'center' }}>
                    <button
                      title="Ver detalhes"
                      onClick={() => setSelected(entry)}
                      style={{
                        background: 'none', border: 'none', cursor: 'pointer',
                        color: 'var(--fg-subtle)', fontSize: 14, padding: '2px 6px',
                        borderRadius: 'var(--radius-sm)', transition: 'color var(--transition)',
                      }}
                      onMouseEnter={e => e.currentTarget.style.color = 'var(--accent)'}
                      onMouseLeave={e => e.currentTarget.style.color = 'var(--fg-subtle)'}
                    >
                      <i className="bi bi-eye" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}

// ─── Dashboard Page ───────────────────────────────────────
function Dashboard() {
  const [stats, setStats]         = useState(null);
  const [historico, setHistorico] = useState([]);
  const [loading, setLoading]     = useState(true);
  const [error, setError]         = useState(null);

  useEffect(() => {
    Promise.all([API.dashboard(), API.historico(20)])
      .then(([dash, hist]) => {
        setStats(dash);
        setHistorico(hist.results);
      })
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (error) {
    return (
      <div className="empty">
        <div className="empty-icon"><i className="bi bi-exclamation-triangle" /></div>
        <p className="empty-title">Erro ao carregar</p>
        <p className="empty-msg">{error}</p>
      </div>
    );
  }

  return (
    <div>
      <div className="page-head">
        <div>
          <h1 className="page-title">Dashboard</h1>
          <p className="page-subtitle">Visão geral do sistema de Controladoria</p>
        </div>
      </div>

      {/* Stat cards */}
      <div className="grid-4" style={{ marginBottom: 20 }}>
        <StatCard icon="bi-clipboard-check"   label="Auditorias" value={stats?.total_auditorias} loading={loading} />
        <StatCard icon="bi-lightning-charge"  label="Ações"      value={stats?.total_acoes}      loading={loading} />
        <StatCard icon="bi-graph-up"          label="Índices"    value={stats?.total_indices}    loading={loading} />
        <StatCard icon="bi-people"            label="Usuários"   value={stats?.total_usuarios}   loading={loading} />
      </div>

      {/* PAINT Pipeline */}
      <PAINTPipeline
        statusData={stats?.auditorias_por_status}
        total={stats?.total_auditorias || 0}
        loading={loading}
      />

      {/* Audit Trail */}
      <AuditTrail entries={historico} loading={loading} />
    </div>
  );
}
