from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, DateField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional


class IncomeForm(FlaskForm):
    category_id = SelectField('Categoria', coerce=int, validators=[DataRequired()])
    amount = DecimalField('Valor (R$)', places=2, validators=[DataRequired(), NumberRange(min=0.01)])
    description = StringField('Descricao', validators=[Optional()])
    source = StringField('Fonte', validators=[Optional()])
    date = DateField('Data', validators=[DataRequired()])
    is_recurring = BooleanField('Receita Recorrente')
    recurrence = SelectField('Frequencia', choices=[
        ('', 'Selecione...'),
        ('weekly', 'Semanal'),
        ('biweekly', 'Quinzenal'),
        ('monthly', 'Mensal'),
    ], validators=[Optional()])
    submit = SubmitField('Salvar')
