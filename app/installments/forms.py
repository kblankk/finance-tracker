from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, IntegerField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional


class InstallmentForm(FlaskForm):
    description = StringField('Descricao', validators=[DataRequired()])
    total_amount = DecimalField('Valor Total das Parcelas (R$)', places=2, validators=[DataRequired(), NumberRange(min=0.01)])
    num_installments = IntegerField('Numero de Parcelas', validators=[DataRequired(), NumberRange(min=2, max=72)])
    additional_per_month = DecimalField('Valor Adicional por Mes (R$)', places=2, default=0, validators=[Optional(), NumberRange(min=0)])
    category_id = SelectField('Categoria', coerce=int, validators=[DataRequired()])
    payee = StringField('Destinatario/Empresa', validators=[Optional()])
    start_date = DateField('Data da Primeira Parcela', validators=[DataRequired()])
    submit = SubmitField('Criar Parcelamento')
