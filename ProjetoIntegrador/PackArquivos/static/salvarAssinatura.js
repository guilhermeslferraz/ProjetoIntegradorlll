document.addEventListener("DOMContentLoaded", function() {
    const canvas = document.getElementById('canvasAssinatura');
    const salvarAssinaturaBtn = document.getElementById('salvarRecibo');
    const botaoLimparAssinatura = document.getElementById('limparAssinatura');
    const signaturePad = new SignaturePad(canvas);

    salvarAssinaturaBtn.addEventListener('click', function(event) {
        event.preventDefault();
        if (signaturePad.isEmpty()) {
            alert('Por favor, assine o recibo.');
            return;
        }

        // Obtém a assinatura em base64
        const assinaturaBase64 = signaturePad.toDataURL();

        // Cria um formulário de envio com a assinatura
        const formData = new FormData();
        formData.append('signature', assinaturaBase64);

        fetch('/uploadAssinatura', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                alert('Assinatura salva com sucesso!');

                // Cria um elemento <a> para fazer o download do PDF
                const linkDownload = document.createElement('a');
                linkDownload.href = data.pdf_path;
                linkDownload.download = 'recibo.pdf';
                document.body.appendChild(linkDownload);
                linkDownload.click();
                document.body.removeChild(linkDownload);
            } else {
                alert('Erro ao salvar a assinatura.');
            }
        })
        .catch(error => {
            console.error('Erro ao salvar a assinatura:', error);
            alert('Erro ao salvar a assinatura. Por favor, tente novamente.');
        });
    });

    botaoLimparAssinatura.addEventListener('click', function (event) {
        event.preventDefault();
        signaturePad.clear();
    });
});
