document.addEventListener('DOMContentLoaded', function() {
    const dataElement = document.getElementById('tipos-acao-data');
    if (!dataElement) return;

    const tiposAcaoData = JSON.parse(dataElement.textContent);
    const tiposAcaoMap = {};
    tiposAcaoData.forEach(item => { tiposAcaoMap[item.id] = item; });

    const tipoAcaoSelect   = document.getElementById('id_tipo_acao');
    const avaliacaoTextarea = document.getElementById('id_avaliacao');
    const conclusaoTextarea = document.getElementById('id_conclusao');

    // Cria o banner de confirmação inline (Perspectiva de Parceiro de Discurso)
    const banner = document.createElement('div');
    banner.id = 'autofill-banner';
    banner.style.cssText = [
        'display:none',
        'background:oklch(0.55 0.18 145/0.1)',
        'border:1px solid oklch(0.55 0.18 145/0.35)',
        'border-radius:var(--radius-sm)',
        'padding:10px 14px',
        'font-size:13px',
        'color:var(--text-secondary)',
        'margin-block-start:8px',
        'gap:12px',
        'align-items:center',
    ].join(';');
    banner.innerHTML = `
        <span style="flex:1"><i class="bi bi-magic" style="margin-inline-end:6px"></i>
        Substituir os textos atuais pelos padrões deste tipo de ação?</span>
        <button type="button" id="autofill-sim"  class="btn btn-primary btn-sm" style="flex-shrink:0">Sim, substituir</button>
        <button type="button" id="autofill-nao"  class="btn btn-ghost  btn-sm" style="flex-shrink:0">Manter atual</button>
    `;
    tipoAcaoSelect.closest('.form-group').appendChild(banner);

    // Cria o toast de confirmação após o preenchimento
    const toast = document.createElement('div');
    toast.id = 'autofill-toast';
    toast.style.cssText = [
        'display:none',
        'background:oklch(0.55 0.18 145/0.12)',
        'border:1px solid oklch(0.55 0.18 145/0.35)',
        'border-radius:var(--radius-sm)',
        'padding:8px 14px',
        'font-size:13px',
        'color:var(--text-secondary)',
        'margin-block-start:8px',
    ].join(';');
    toast.innerHTML = '<i class="bi bi-check2-circle" style="margin-inline-end:6px;color:var(--success)"></i>Campos preenchidos com o padrão do tipo selecionado.';
    tipoAcaoSelect.closest('.form-group').appendChild(toast);

    let pendingData = null;

    function applyAutofill(data) {
        avaliacaoTextarea.value = data.mensagem_padrao_avaliacao || '';
        conclusaoTextarea.value = data.mensagem_padrao_conclusao || '';
        banner.style.display = 'none';
        toast.style.display  = 'block';
        clearTimeout(toast._hideTimer);
        toast._hideTimer = setTimeout(() => { toast.style.display = 'none'; }, 3500);
    }

    tipoAcaoSelect.addEventListener('change', function() {
        const selectedId = this.value;
        toast.style.display = 'none';
        banner.style.display = 'none';

        if (!selectedId || !tiposAcaoMap[selectedId]) return;

        const data = tiposAcaoMap[selectedId];
        const temConteudo = avaliacaoTextarea.value.trim() !== '' || conclusaoTextarea.value.trim() !== '';

        if (temConteudo) {
            // Mostra confirmação inline em vez do confirm() nativo
            pendingData = data;
            banner.style.display = 'flex';
        } else {
            applyAutofill(data);
        }
    });

    document.getElementById('autofill-sim').addEventListener('click', function() {
        if (pendingData) applyAutofill(pendingData);
        pendingData = null;
    });

    document.getElementById('autofill-nao').addEventListener('click', function() {
        banner.style.display = 'none';
        pendingData = null;
    });
});
