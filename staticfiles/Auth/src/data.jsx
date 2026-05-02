// Camada de acesso à API Django
const API = {
  async _get(url) {
    const res = await fetch(url, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
      credentials: 'same-origin',
    });
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    return res.json();
  },

  dashboard:  () => API._get('/api/dashboard/'),
  historico:  (limit = 20) => API._get(`/api/historico/?limit=${limit}`),
  auditorias: () => API._get('/api/auditorias/'),
  acoes:      () => API._get('/api/acoes/'),
};

// Labels e cores para o pipeline PAINT
const PAINT_STAGES = [
  { key: 'PLANEJADA',    letter: 'P', label: 'Planejadas',    color: '#6366f1' },
  { key: 'EM_ANDAMENTO', letter: 'A', label: 'Em Andamento',  color: '#f59e0b' },
  { key: 'CONCLUIDA',    letter: 'I', label: 'Concluídas',    color: '#10b981' },
  { key: 'CANCELADA',    letter: 'C', label: 'Canceladas',    color: '#ef4444' },
];

const STATUS_BADGE = {
  PLANEJADA:    { cls: 'badge-accent',   label: 'Planejada'    },
  EM_ANDAMENTO: { cls: 'badge-warning',  label: 'Em Andamento' },
  CONCLUIDA:    { cls: 'badge-success',  label: 'Concluída'    },
  CANCELADA:    { cls: 'badge-danger',   label: 'Cancelada'    },
};

const TIPO_ICON = {
  Usuario:        'bi-person',
  Acao:           'bi-lightning-charge',
  Auditoria:      'bi-clipboard-check',
  MatrizAuditoria:'bi-grid-3x3',
  Indice:         'bi-graph-up',
  TipoAcao:       'bi-tag',
  TipoIndice:     'bi-layers',
  GrupoIndice:    'bi-collection',
};
