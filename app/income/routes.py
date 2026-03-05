import csv
import io
from datetime import date
from flask import render_template, redirect, url_for, flash, request, Response
from flask_login import login_required, current_user
from app.income import income_bp
from app.income.forms import IncomeForm
from app.extensions import db
from app.models.income import Income
from app.models.category import Category


@income_bp.route('/')
@login_required
def list():
    page = request.args.get('page', 1, type=int)
    date_from = request.args.get('date_from', type=str)
    date_to = request.args.get('date_to', type=str)
    category_id = request.args.get('category_id', type=int)
    amount_min = request.args.get('amount_min', type=float)
    amount_max = request.args.get('amount_max', type=float)
    search = request.args.get('search', type=str)

    query = Income.query.filter_by(user_id=current_user.id)

    if date_from:
        query = query.filter(Income.date >= date.fromisoformat(date_from))
    if date_to:
        query = query.filter(Income.date <= date.fromisoformat(date_to))
    if category_id:
        query = query.filter_by(category_id=category_id)
    if amount_min is not None:
        query = query.filter(Income.amount >= amount_min)
    if amount_max is not None:
        query = query.filter(Income.amount <= amount_max)
    if search:
        query = query.filter(
            db.or_(
                Income.description.ilike(f'%{search}%'),
                Income.source.ilike(f'%{search}%'),
            )
        )

    incomes = query.order_by(Income.date.desc()).paginate(page=page, per_page=10)
    categories = _get_income_categories()
    filters = {
        'date_from': date_from, 'date_to': date_to,
        'category_id': category_id, 'amount_min': amount_min,
        'amount_max': amount_max, 'search': search,
    }
    return render_template('income/list.html',
        incomes=incomes, categories=categories, filters=filters)


@income_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = IncomeForm()
    form.category_id.choices = _get_income_categories()

    if form.validate_on_submit():
        income = Income(
            user_id=current_user.id,
            category_id=form.category_id.data,
            amount=form.amount.data,
            description=form.description.data,
            source=form.source.data,
            date=form.date.data,
            is_recurring=form.is_recurring.data,
            recurrence=form.recurrence.data if form.is_recurring.data else None,
        )
        db.session.add(income)
        db.session.commit()
        flash('Receita adicionada com sucesso!', 'success')
        return redirect(url_for('transactions.list'))

    return render_template('income/form.html', form=form, title='Nova Receita')


@income_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    income = Income.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = IncomeForm(obj=income)
    form.category_id.choices = _get_income_categories()

    if form.validate_on_submit():
        income.category_id = form.category_id.data
        income.amount = form.amount.data
        income.description = form.description.data
        income.source = form.source.data
        income.date = form.date.data
        income.is_recurring = form.is_recurring.data
        income.recurrence = form.recurrence.data if form.is_recurring.data else None
        db.session.commit()
        flash('Receita atualizada!', 'success')
        return redirect(url_for('transactions.list'))

    return render_template('income/form.html', form=form, title='Editar Receita')


@income_bp.route('/toggle-received/<int:id>', methods=['POST'])
@login_required
def toggle_received(id):
    income = Income.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    income.is_received = not income.is_received
    db.session.commit()
    flash('Receita confirmada!' if income.is_received else 'Receita desmarcada.', 'success')
    next_url = request.form.get('next') or url_for('income.list')
    return redirect(next_url)


@income_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    income = Income.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(income)
    db.session.commit()
    flash('Receita removida.', 'success')
    return redirect(request.referrer or url_for('transactions.list'))


@income_bp.route('/export-csv')
@login_required
def export_csv():
    incomes = Income.query.filter_by(user_id=current_user.id).order_by(Income.date.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Data', 'Descricao', 'Categoria', 'Fonte', 'Valor'])
    for inc in incomes:
        writer.writerow([
            inc.date.strftime('%d/%m/%Y'),
            inc.description or '',
            inc.category.name if inc.category else '',
            inc.source or '',
            f'{inc.amount:.2f}',
        ])
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=receitas.csv'},
    )


def _get_income_categories():
    cats = Category.query.filter(
        Category.type == 'income',
        db.or_(Category.user_id == current_user.id, Category.user_id == None)
    ).all()
    return [(c.id, c.name) for c in cats]
