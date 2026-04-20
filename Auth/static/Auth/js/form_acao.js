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

    // Adiciona um "escutador" que dispara uma função sempre que o select for alterado.
    tipoAcaoSelect.addEventListener('change', function() {
        const selectedId = this.value;
        if (selectedId && tiposAcaoMap[selectedId]) {
            const data = tiposAcaoMap[selectedId];
            avaliacaoTextarea.value = data.mensagem_padrao_avaliacao || '';
            conclusaoTextarea.value = data.mensagem_padrao_conclusao || '';
        } else {
            avaliacaoTextarea.value = '';
            conclusaoTextarea.value = '';
        }
    });
});