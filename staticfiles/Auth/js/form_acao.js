// Espera todo o conteúdo do HTML ser carregado antes de executar o script.
document.addEventListener('DOMContentLoaded', function() {
    
    // Pega o elemento <script> que o Django criou com os dados.
    const dataElement = document.getElementById('tipos-acao-data');

    // Se o elemento com os dados não existir na página, o script para aqui.
    if (!dataElement) {
        return;
    }

    // Lê o conteúdo JSON de dentro do elemento.
    const tiposAcaoData = JSON.parse(dataElement.textContent);

    // Mapeia os dados para um formato mais fácil de usar (ID -> objeto).
    const tiposAcaoMap = {};
    tiposAcaoData.forEach(item => {
        tiposAcaoMap[item.id] = item;
    });

    // Pega os elementos do formulário do DOM.
    const tipoAcaoSelect = document.getElementById('id_tipo_acao');
    const avaliacaoTextarea = document.getElementById('id_avaliacao');
    const conclusaoTextarea = document.getElementById('id_conclusao');

    tipoAcaoSelect.addEventListener('change', function() {
        const selectedId = this.value;
        if (!selectedId || !tiposAcaoMap[selectedId]) return;

        const data = tiposAcaoMap[selectedId];
        const avaliacaoVazia = avaliacaoTextarea.value.trim() === '';
        const conclusaoVazia = conclusaoTextarea.value.trim() === '';

        if (!avaliacaoVazia || !conclusaoVazia) {
            const confirmar = confirm(
                'Deseja substituir o texto atual pelos valores padrão deste tipo de ação?'
            );
            if (!confirmar) return;
        }

        avaliacaoTextarea.value = data.mensagem_padrao_avaliacao || '';
        conclusaoTextarea.value = data.mensagem_padrao_conclusao || '';
    });
});