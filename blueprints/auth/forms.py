"""
blueprints/auth/forms.py

Flask-WTF gera automaticamente o token CSRF em cada formulário e valida
no submit - não é preciso escrever essa lógica manualmente.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField("Usuário", validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField("Senha", validators=[DataRequired()])
    submit = SubmitField("Entrar")
