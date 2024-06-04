import secrets
import base64
import os
from urllib import request
from PIL import Image
from flask import render_template, flash, redirect, request, url_for, jsonify, session, send_file
from flask_login import login_user, logout_user, current_user, login_required
from PackArquivos import bcrypt
from PackArquivos.forms import LoginForm, CriarContaForm, GerarReciboForm
from PackArquivos.models import *
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from random import randint
from num2words import num2words


@app.route('/login', methods=['GET', 'POST'])
def login():
    formLogin = LoginForm()
    if formLogin.validate_on_submit():
        usuario = Usuario.query.filter_by(email=formLogin.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, formLogin.senha.data):
            login_user(usuario, remember=formLogin.lembrar_dados.data)
            flash(f'Logado com sucesso! Bem-vindo {usuario.nome}', 'alert-success')
            par_next = request.args.get('next')
            if par_next:
                return redirect(par_next)
            else:
                return redirect(url_for('index'))
        else:
            flash('Falha no login! E-mail ou senha incorretos.', 'alert-danger')
    return render_template('login.html', formLogin=formLogin)


@app.route('/criarConta', methods=['GET', 'POST'])
def criarConta():
    formCriarConta = CriarContaForm()
    if formCriarConta.validate_on_submit():
        senhaCrypt = bcrypt.generate_password_hash(formCriarConta.senha.data).decode('utf-8')
        usuario = Usuario(nome=formCriarConta.nome.data, sobrenome=formCriarConta.sobrenome.data,
                          email=formCriarConta.email.data, senha=senhaCrypt)
        db.session.add(usuario)
        db.session.commit()
        login_user(usuario, remember=formCriarConta.senha.data)
        flash(f'Conta criada com sucesso para o usuario {usuario.nome}!', 'alert-success')
        return redirect(url_for('index'))
    return render_template('criarConta.html', formCriarConta=formCriarConta)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/sobre')
def sobre():
    return render_template('sobre.html')


@app.route('/gerarRecibo', methods=['GET', 'POST'])
@login_required
def gerarRecibo():
    formGerarRecibo = GerarReciboForm()
    if formGerarRecibo.validate_on_submit():
        session['dadosPDF'] = {
            'empresa': current_user.nome,
            'numero': formGerarRecibo.numero.data,
            'valor': formGerarRecibo.valor.data,
            'valorExtenso': formGerarRecibo.valorExtenso.data,
            'data': formGerarRecibo.data.data.strftime('%d/%m/%Y'),
            'nome': formGerarRecibo.nome.data,
            'cpf': formGerarRecibo.cpf.data,
            'descricao': formGerarRecibo.descricao.data
        }
        return redirect(url_for('salvarAssinatura'))
    elif request.method == 'GET':
        formGerarRecibo.empresa.data = current_user.nome
    return render_template('gerarRecibo.html', formGerarRecibo=formGerarRecibo)


@app.route('/valor_extenso', methods=['POST'])
def valor_extenso():
    data = request.json
    valor = data.get('valor', '0')
    valor = valor.replace("R$ ", "")
    return jsonify({'valorExtenso': "R$ " + num2words(valor, lang='pt_BR') + " reais"})


@app.route('/salvarAssinatura', methods=['GET', 'POST'])
@login_required
def salvarAssinatura():
    formGerarRecibo = GerarReciboForm()
    dadosPDF = session.get('dadosPDF')

    if dadosPDF:
        formGerarRecibo.empresa.data = dadosPDF.get('empresa')
        formGerarRecibo.numero.data = dadosPDF.get('numero')
        formGerarRecibo.valor.data = dadosPDF.get('valor')
        formGerarRecibo.valorExtenso.data = dadosPDF.get('valorExtenso')
        formGerarRecibo.data.data = dadosPDF.get('data')
        formGerarRecibo.nome.data = dadosPDF.get('nome')
        formGerarRecibo.cpf.data = dadosPDF.get('cpf')
        formGerarRecibo.descricao.data = dadosPDF.get('descricao')

    if 'salvarRecibo' in request.form:
        # Definir o caminho e o nome do arquivo
        directory = './static/arquivosPDF'
        filename = "recibo_"

        path = os.path.join(directory, filename)

        # Criar o diretório se não existir
        os.makedirs(directory, exist_ok=True)
        return criar_recibo_pdf(path, dadosPDF)

    return render_template('salvarAssinatura.html', formGerarRecibo=formGerarRecibo, dadosPDF=dadosPDF)


@app.route('/uploadAssinatura', methods=['POST'])
def upload_assinatura():
    assinatura_base64 = request.form['signature']
    assinatura_data = assinatura_base64.split(',')[1]
    assinatura_bin = base64.b64decode(assinatura_data)

    # Salva a imagem da assinatura no diretório local
    assinatura_path = os.path.join('.', 'PackArquivos', 'static', 'arquivosPDF', 'assinatura.png')
    os.makedirs(os.path.dirname(assinatura_path), exist_ok=True)
    with open(assinatura_path, 'wb') as f:
        f.write(assinatura_bin)

    # Abre a imagem
    assinatura_img = Image.open(assinatura_path)

    # Cria uma nova imagem com fundo branco do mesmo tamanho da imagem original
    imagem_com_fundo_branco = Image.new("RGBA", assinatura_img.size, "white")

    # Combina as imagens, mantendo a assinatura sobre o fundo branco
    imagem_final = Image.alpha_composite(imagem_com_fundo_branco, assinatura_img)

    # Salva a imagem final com fundo branco
    assinatura_com_fundo_path = os.path.join('.', 'PackArquivos', 'static', 'arquivosPDF', 'assinatura.png')
    imagem_final.save(assinatura_com_fundo_path)

    # Chame a função criar_recibo_pdf após salvar a assinatura
    dadosPDF = session.get('dadosPDF')
    if dadosPDF:
        # Defina o caminho e o nome do arquivo PDF
        directory = './PackArquivos/static/arquivosPDF'
        tokenPDF = secrets.token_hex(8)
        filename = f"recibo_{tokenPDF}.pdf"
        path = os.path.join(directory, filename)

        # Criar o diretório se não existir
        os.makedirs(directory, exist_ok=True)

        # Chamar a função criar_recibo_pdf para gerar o PDF
        criar_recibo_pdf(filename=path, dadosPDF=dadosPDF)

        # Gerar a URL para acessar o PDF
        pdfGerado = criar_recibo_pdf(filename=path, dadosPDF=dadosPDF)

        # Retornar o caminho do arquivo PDF gerado
        return jsonify(success=True, pdf_path=pdf_url)

    return jsonify(success=False, error='Dados do formulário não encontrados')


def criar_recibo_pdf(filename, dadosPDF):
    c = canvas.Canvas(filename, pagesize=landscape(letter))
    width, height = landscape(letter)

    # Definindo margens
    margin_x = 0.5 * inch
    margin_y = 0.7 * inch  # Reduzindo a margem superior

    # Definindo a largura e altura do retângulo
    rect_width = width - 2 * margin_x
    rect_height = height - 2 * margin_y

    # Adicionar retângulo ao redor do recibo
    c.rect(margin_x, margin_y, rect_width, rect_height)

    # Título
    c.setFont("Helvetica-Bold", 44)
    c.drawCentredString(width / 5, height - margin_y - 0.8 * inch, "RECIBO")

    # Data e local de emissão
    c.setFont("Times-Roman", 20)
    c.setFillColorRGB(0.5, 0.5, 0.5)  # Cor cinza
    c.drawRightString(width / 2.54 - 0.5 * inch, height - margin_y - 1.4 * inch, "Local e data de emissão: ")
    c.setFillColorRGB(0, 0, 0)  # Voltando para preto
    c.setFont("Helvetica", 20)
    c.drawCentredString(width / 5.20, height - margin_y - 2.5 * inch, f"Data:  {(dadosPDF['data'])}")

    # Calculando a posição para o texto "Nº"
    num_recibo_text = f"Nº {dadosPDF['numero']}"
    num_recibo_width = c.stringWidth(num_recibo_text, "Helvetica", 20)
    num_recibo_x = width - margin_x - num_recibo_width
    num_recibo_y = height - margin_y - 0.7 * inch

    # Desenhando o texto "Nº" na margem direita
    c.drawString(num_recibo_x, num_recibo_y, num_recibo_text)

    # Recebido de
    c.drawString(margin_x + 0.5 * inch, height - margin_y - 3 * inch, f"Recebi de: {dadosPDF['empresa']}")
    c.drawString(margin_x + 5.8 * inch, height - margin_y - 3 * inch,
                 f"a quantia de: {dadosPDF['valor']}")

    # Quantia por extenso
    c.drawString(margin_x + 0.5 * inch, height - margin_y - 3.5 * inch, "Quantia por extenso:")
    c.roundRect(margin_x + 0.5 * inch, height - margin_y - 4.5 * inch, 9 * inch, 0.8 * inch, 0.1 * inch)
    c.drawString(margin_x + 0.6 * inch, height - margin_y - 4.3 * inch, f"{dadosPDF['valorExtenso']}")

    # Conceito
    c.drawString(margin_x + 0.5 * inch, height - margin_y - 5 * inch,
                 f"Referente a: {dadosPDF['descricao']}")
    c.drawString(margin_x + 0.5 * inch, height - margin_y - 5.5 * inch,
                 "__________________________________________________________")

    # Nome e assinatura
    signature_text = "Nome e assinatura do recebedor"
    signature_text_width = c.stringWidth(signature_text, "Times-Roman", 14)
    signature_text_x = margin_x + (rect_width - signature_text_width) / 2
    c.setFont("Times-Roman", 18)
    c.setFillColorRGB(0.5, 0.5, 0.5)  # Cor cinza
    c.drawCentredString(width / 2, height - margin_y - 7 * inch, signature_text)
    c.setFillColorRGB(0, 0, 0)  # Voltando para preto

    # Adicionar a imagem da assinatura
    image_width = 150
    image_height = 70
    image_x = (width - image_width) / 2
    image_y = height - margin_y - 6.6 * inch
    c.drawImage("./PackArquivos/static/arquivosPDF/assinatura.png", image_x, image_y,
                width=image_width, height=image_height)

    c.line(margin_x + 2 * inch, height - margin_y - 6.6 * inch, margin_x + rect_width - 2 * inch,
           height - margin_y - 6.6 * inch)

    c.save()


@app.route('/listarRecibos', methods=['GET', 'POST'])
def listarRecibos():
    return render_template('listarRecibos.html')


@app.route('/perfil')
@login_required
def perfil():
    foto_perfil = url_for('static', filename='fotos_perfil/{}'.format(current_user.foto_perfil))
    return render_template('perfil.html', foto_perfil=foto_perfil)


@app.route('/editarperfil')
@login_required
def editarPerfil():
    foto_perfil = url_for('static', filename='fotos_perfil/{}'.format(current_user.foto_perfil))
    return render_template('editarPerfil.html', foto_perfil=foto_perfil)


@app.route('/registros', methods=['GET', 'POST'])
@login_required
def registros():
    return render_template('registros.html')


@app.route('/sair')
@login_required
def sair():
    logout_user()
    return redirect(url_for('login'))
