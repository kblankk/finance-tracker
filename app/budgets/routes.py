from datetime import date
from decimal import Decimal
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import func, extract
from app.budgets import budgets_bp
from app.budgets.forms import BudgetForm
from app.extensions import db
from app.models.budget import Budget
from app.models.expense import Expense
from app.models.category import Category


@budgets_bp.route('/')
@login_required
def list():
    today = date.today()
    month = request.args.get('month', today.month, type=int)
    year = request.args.get('year', today.year, type=int)

    budgets = Budget.query.filter_by(
        user_id=current_user.id, month=month, year=year
    ).all()

    budget_data = []
    for b in budgets:
        spent = db.session.query(func.sum(Expense.amount)).filter(
            Expense.user_id == current_user.id,
            Expense.category_id == b.category_id,
            extract('month', Expense.due_date) == month,
            extract('year', Expense.due_date) == year,
        ).scalar() or Decimal('0')
        pct = min(float(spent / b.amount_limit) * 100, 100) if b.amount_limit > 0 else 0
        available = b.amount_limit - spent
        budget_data.append({
            'budget': b,
            'spent': spent,
            'available': available,
            'pct': pct,
            'over': spent > b.amount_limit,
        })

    return render_template('budgets/list.html',
        budget_data=budget_data, month=month, year=year)


@budgets_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = BudgetForm()
    form.category_id.choices = _get_expense_categories()
    today = date.today()
    if request.method == 'GET':
        form.month.data = today.month
        form.year.data = today.year

    if form.validate_on_submit():
        existing = Budget.query.filter_by(
            user_id=current_user.id,
            category_id=form.category_id.data,
            month=form.month.data,
            year=form.year.data,
        ).first()
        if existing:
            flash('Ja existe um orcamento para esta categoria neste mes.', 'warning')
            return render_template('budgets/form.html', form=form, title='Novo Orcamento')

        budget = Budget(
            user_id=current_user.id,
            category_id=form.category_id.data,
            amount_limit=form.amount_limit.data,
            month=form.month.data,
            year=form.year.data,
        )
        db.session.add(budget)
        db.session.commit()
        flash('Orcamento criado com sucesso!', 'success')
        return redirect(url_for('budgets.list'))

    return render_template('budgets/form.html', form=form, title='Novo Orcamento')


@budgets_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    budget = Budget.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = BudgetForm(obj=budget)
    form.category_id.choices = _get_expense_categories()

    if form.validate_on_submit():
        budget.category_id = form.category_id.data
        budget.amount_limit = form.amount_limit.data
        budget.month = form.month.data
        budget.year = form.year.data
        db.session.commit()
        flash('Orcamento atualizado!', 'success')
        return redirect(url_for('budgets.list'))

    return render_template('budgets/form.html', form=form, title='Editar Orcamento')


@budgets_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    budget = Budget.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(budget)
    db.session.commit()
    flash('Orcamento removido.', 'success')
    return redirect(url_for('budgets.list'))


@budgets_bp.route('/spend/<int:id>', methods=['POST'])
@login_required
def spend(id):
    budget = Budget.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    amount = request.form.get('amount', type=float)
    description = request.form.get('description', '').strip()

    if not amount or amount <= 0:
        flash('Informe um valor valido.', 'warning')
        return redirect(url_for('budgets.list', month=budget.month, year=budget.year))

    expense = Expense(
        user_id=current_user.id,
        category_id=budget.category_id,
        amount=amount,
        description=description or None,
        due_date=date.today(),
        is_paid=True,
        priority='normal',
    )
    db.session.add(expense)
    db.session.commit()
    flash(f'Gasto de R$ {amount:.2f} registrado!', 'success')
    return redirect(url_for('budgets.list', month=budget.month, year=budget.year))


def _get_expense_categories():
    cats = Category.query.filter(
        Category.type == 'expense',
        db.or_(Category.user_id == current_user.id, Category.user_id == None)
    ).all()
    return [(c.id, c.name) for c in cats]
