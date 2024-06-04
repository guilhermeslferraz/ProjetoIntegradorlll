document.addEventListener("DOMContentLoaded", function () {
    const formularioRecibo = document.getElementById('formularioRecibo');
    const LimparFormulario = document.getElementById('clearRecibo');
    const submitRecibo = document.getElementById('submitRecibo');


    function limparFormulario() {
        formularioRecibo.reset();
    }

    function init() {
        LimparFormulario.addEventListener('click', function (event) {
            event.preventDefault(); // Impede o comportamento padrão do botão
            limparFormulario();
        });
    }

    // Inicializa os elementos do DOM
    init();

});
