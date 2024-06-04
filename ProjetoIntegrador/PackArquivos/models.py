from datetime import datetime, timedelta
from pytz import timezone
from PackArquivos import app, db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_usuario(id_usuario):
    return Usuario.query.get(id_usuario)


def horarioCriado():
    # Define o fuso horário de Brasília
    brasilia_timezone = timezone('America/Sao_Paulo')

    # Obtém a data e hora atual em Brasília
    return datetime.now(brasilia_timezone)


class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    sobrenome = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(80), nullable=False)
    foto_perfil = db.Column(db.String(80), default='/static/fotos_perfil/default.jpg')
    recibo = db.relationship('Recibo', backref='usuario', lazy=True)


class Recibo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    empresa = db.Column(db.String(80), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    data = db.Column(db.DateTime, nullable=False, default=horarioCriado)
    nome = db.Column(db.String(80), nullable=False)
    cpf = db.Column(db.String(80), nullable=False)
    descricao = db.Column(db.String(80), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)


with app.app_context():
    db.create_all()
