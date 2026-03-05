from flask_wtf import FlaskForm
from wtforms import SelectField, DecimalField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class BudgetForm(FlaskForm):
    category_id = SelectField('Categoria', coerce=int, validators=[DataRequired()])
    amount_limit = DecimalField('Limite (R$)', places=2, validators=[DataRequired(), NumberRange(min=0.01)])
    month = SelectField('Mês', coerce=int, choices=[
        (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'),
        (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'),
        (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro'),
    ], validators=[DataRequired()])
    year = IntegerField('Ano', validators=[DataRequired(), NumberRange(min=2020, max=2099)])
    submit = SubmitField('Salvar')
