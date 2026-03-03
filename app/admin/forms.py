from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional, ValidationError
from app.models.user import User


class EditUserForm(FlaskForm):
    username = StringField('Nome de usuario', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Funcao', choices=[('user', 'Usuario'), ('admin', 'Administrador')])
    submit = SubmitField('Salvar')

    def __init__(self, original_user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_user = original_user

    def validate_username(self, field):
        if field.data != self.original_user.username:
            if User.query.filter_by(username=field.data).first():
                raise ValidationError('Este nome de usuario ja esta em uso.')

    def validate_email(self, field):
        if field.data != self.original_user.email:
            if User.query.filter_by(email=field.data).first():
                raise ValidationError('Este email ja esta cadastrado.')


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField('Nova Senha', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Resetar Senha')
