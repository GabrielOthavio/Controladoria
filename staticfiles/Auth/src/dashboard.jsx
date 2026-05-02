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

// ─── Audit Trail ──────────────────────────────────────────
function AuditTrail({ entries, loading }) {
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
                  {entry.descricao}
                </td>
                <td style={{ fontSize: 12, color: 'var(--fg-muted)' }}>
                  {entry.usuario === 'Sistema'
                    ? <span style={{ color: 'var(--fg-subtle)', fontStyle: 'italic' }}>Sistema</span>
                    : entry.usuario}
                </td>
                <td className="right num" style={{ fontSize: 12, color: 'var(--fg-subtle)', whiteSpace: 'nowrap' }}>
                  {entry.data_hora}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
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
