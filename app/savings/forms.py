from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional


class SavingsGoalForm(FlaskForm):
    name = StringField('Nome da Meta', validators=[DataRequired()])
    target_amount = DecimalField('Valor Alvo (R$)', places=2, validators=[DataRequired(), NumberRange(min=0.01)])
    deadline = DateField('Prazo', validators=[Optional()])
    icon = SelectField('Icone', choices=[
        ('bi-piggy-bank', 'Cofrinho'),
        ('bi-house', 'Casa'),
        ('bi-car-front', 'Carro'),
        ('bi-airplane', 'Viagem'),
        ('bi-mortarboard', 'Educacao'),
        ('bi-phone', 'Eletronico'),
        ('bi-heart', 'Saude'),
        ('bi-gift', 'Presente'),
    ], validators=[Optional()])
    color = StringField('Cor', default='#0d6efd', validators=[Optional()])
    submit = SubmitField('Salvar')


class ContributionForm(FlaskForm):
    amount = DecimalField('Valor (R$)', places=2, validators=[DataRequired(), NumberRange(min=0.01)])
    description = StringField('Descricao', validators=[Optional()])
    date = DateField('Data', validators=[DataRequired()])
    submit = SubmitField('Adicionar')
