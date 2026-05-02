// ─── Auditorias List ──────────────────────────────────────
function AuditoriasList() {
  const [data, setData]       = React.useState([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    API.auditorias()
      .then(res => setData(res.results))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div className="page-head">
        <div>
          <h1 className="page-title">Auditorias</h1>
          <p className="page-subtitle">Acompanhamento do ciclo PAINT</p>
        </div>
        <div className="page-actions">
          <a href="/auditorias/adicionar/" className="btn btn-primary">
            <i className="bi bi-plus-lg" /> Nova Auditoria
          </a>
        </div>
      </div>

      <div className="card">
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Nome</th>
                <th>Status</th>
                <th>Início</th>
                <th>Conclusão</th>
                <th className="right">Apuração Inicial</th>
                <th className="right">Apuração Final</th>
                <th className="right">RCD</th>
              </tr>
            </thead>
            <tbody>
              {loading
                ? Array.from({ length: 6 }).map((_, i) => (
                    <tr key={i}>
                      {Array.from({ length: 7 }).map((__, j) => (
                        <td key={j}><div className="skel" style={{ height: 16, width: '80%' }} /></td>
                      ))}
                    </tr>
                  ))
                : data.length === 0
                ? (
                  <tr>
                    <td colSpan={7}>
                      <div className="empty">
                        <div className="empty-icon"><i className="bi bi-clipboard" /></div>
                        <p className="empty-title">Nenhuma auditoria cadastrada</p>
                      </div>
                    </td>
                  </tr>
                )
                : data.map(a => {
                    const badge = STATUS_BADGE[a.status] || { cls: 'badge', label: a.status };
                    return (
                      <tr key={a.id}>
                        <td style={{ fontWeight: 500 }}>{a.nome}</td>
                        <td><span className={`badge ${badge.cls}`}>{badge.label}</span></td>
                        <td style={{ color: 'var(--fg-muted)', fontSize: 12 }}>{a.data_inicio || '—'}</td>
                        <td style={{ color: 'var(--fg-muted)', fontSize: 12 }}>{a.data_conclusao || '—'}</td>
                        <td className="right num" style={{ color: 'var(--fg-muted)' }}>{a.apuracao_inicial ? `R$ ${a.apuracao_inicial}` : '—'}</td>
                        <td className="right num" style={{ color: 'var(--fg-muted)' }}>{a.apuracao_final ? `R$ ${a.apuracao_final}` : '—'}</td>
                        <td className={`right num ${a.resultado_calculado ? (parseFloat(a.resultado_calculado) >= 0 ? '' : '') : ''}`}
                            style={{ color: a.resultado_calculado ? (parseFloat(a.resultado_calculado) < 0 ? 'var(--danger)' : 'var(--success)') : 'var(--fg-subtle)' }}>
                          {a.resultado_calculado ? `R$ ${a.resultado_calculado}` : '—'}
                        </td>
                      </tr>
                    );
                  })
              }
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// ─── Ações List ───────────────────────────────────────────
function AcoesList() {
  const [data, setData]       = React.useState([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    API.acoes()
      .then(res => setData(res.results))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div className="page-head">
        <div>
          <h1 className="page-title">Ações</h1>
          <p className="page-subtitle">Registro de ações realizadas</p>
        </div>
        <div className="page-actions">
          <a href="/acoes/adicionar/" className="btn btn-primary">
            <i className="bi bi-plus-lg" /> Nova Ação
          </a>
        </div>
      </div>

      <div className="card">
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Identificação</th>
                <th>Tipo de Ação</th>
                <th>Responsável</th>
                <th className="right">Data de Execução</th>
              </tr>
            </thead>
            <tbody>
              {loading
                ? Array.from({ length: 6 }).map((_, i) => (
                    <tr key={i}>
                      {Array.from({ length: 4 }).map((__, j) => (
                        <td key={j}><div className="skel" style={{ height: 16, width: '75%' }} /></td>
                      ))}
                    </tr>
                  ))
                : data.length === 0
                ? (
                  <tr><td colSpan={4}>
                    <div className="empty">
                      <div className="empty-icon"><i className="bi bi-lightning" /></div>
                      <p className="empty-title">Nenhuma ação cadastrada</p>
                    </div>
                  </td></tr>
                )
                : data.map(a => (
                    <tr key={a.id}>
                      <td style={{ fontWeight: 500 }}>{a.identificacao}</td>
                      <td><span className="badge"><i className="bi bi-tag" />{a.tipo_acao}</span></td>
                      <td style={{ color: 'var(--fg-muted)' }}>{a.usuario}</td>
                      <td className="right num" style={{ color: 'var(--fg-muted)', fontSize: 12 }}>{a.data_execucao}</td>
                    </tr>
                  ))
              }
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// ─── Placeholder para views ainda em Django templates ─────
function DjangoRedirect({ label, href }) {
  React.useEffect(() => { window.location.href = href; }, [href]);
  return (
    <div className="empty" style={{ paddingTop: 80 }}>
      <div className="empty-icon"><i className="bi bi-arrow-right-circle" /></div>
      <p className="empty-title">Redirecionando para {label}…</p>
    </div>
  );
}
