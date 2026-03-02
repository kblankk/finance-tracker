from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, DateField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional


class ExpenseForm(FlaskForm):
    category_id = SelectField('Categoria', coerce=int, validators=[DataRequired()])
    amount = DecimalField('Valor (R$)', places=2, validators=[DataRequired(), NumberRange(min=0.01)])
    description = StringField('Descricao', validators=[Optional()])
    payee = StringField('Destinatario/Empresa', validators=[Optional()])
    due_date = DateField('Data de Vencimento', validators=[DataRequired()])
    is_paid = BooleanField('Ja foi paga')
    is_recurring = BooleanField('Despesa Recorrente')
    recurrence = SelectField('Frequencia', choices=[
        ('', 'Selecione...'),
        ('weekly', 'Semanal'),
        ('biweekly', 'Quinzenal'),
        ('monthly', 'Mensal'),
    ], validators=[Optional()])
    priority = SelectField('Prioridade', choices=[
        ('low', 'Baixa'),
        ('normal', 'Normal'),
        ('high', 'Alta'),
    ], validators=[DataRequired()])
    submit = SubmitField('Salvar')
