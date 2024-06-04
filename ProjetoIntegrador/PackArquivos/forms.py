from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, PasswordField, SubmitField, BooleanField, TextAreaField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from flask_login import current_user
from PackArquivos.models import *
from datetime import date
from random import randint


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    lembrar_dados = BooleanField('Manter Acesso?')
    submitLogin = SubmitField('Login')


class CriarContaForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    sobrenome = StringField('Sobrenome', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    confirmar_email = StringField('Confirmar e-mail', validators=[DataRequired(), EqualTo('email')])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(6,20)])
    confirmar_senha = PasswordField('Confirmar senha', validators=[DataRequired(), EqualTo('senha')])
    submitCriarConta = SubmitField('Crie sua conta')

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError("E-mail já cadastrado. Cadastre-se com outro e-mail ou faça login para continuar.")


class GerarReciboForm(FlaskForm):
    empresa = StringField('Empresa', validators=[DataRequired()])
    numero = StringField('Numero', validators=[DataRequired()], render_kw={'readonly': True, "value": randint(0, 9999)})
    valor = StringField('Valor', validators=[DataRequired()], render_kw={"value": "R$ "})
    valorExtenso = StringField('Valor Ext.', validators=[DataRequired()], render_kw={'readonly': True})
    data = DateField('Data', validators=[DataRequired()], render_kw={"value": date.today()})
    nome = StringField('Nome', validators=[DataRequired()])
    cpf = StringField('CPF', validators=[DataRequired()])
    descricao = TextAreaField('Descrição', validators=[DataRequired()])
    submitRecibo = SubmitField('Gerar recibo')
    clearRecibo = SubmitField('Limpar recibo')
    limparAssinatura = SubmitField('Limpar assinatura')
    salvarRecibo = SubmitField('Salvar recibo')
    voltarRecibo = SubmitField('Voltar ao formulário')
