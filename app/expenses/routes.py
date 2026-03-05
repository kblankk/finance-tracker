import csv
import io
from datetime import date
from flask import render_template, redirect, url_for, flash, request, Response
from flask_login import login_required, current_user
from sqlalchemy import and_, or_, func
from app.expenses import expenses_bp
from app.expenses.forms import ExpenseForm
from app.extensions import db
from app.models.expense import Expense
from app.models.category import Category


@expenses_bp.route('/')
@login_required
def list():
    page = request.args.get('page', 1, type=int)
    filter_status = request.args.get('status', 'all')
    date_from = request.args.get('date_from', type=str)
    date_to = request.args.get('date_to', type=str)
    category_id = request.args.get('category_id', type=int)
    amount_min = request.args.get('amount_min', type=float)
    amount_max = request.args.get('amount_max', type=float)
    search = request.args.get('search', type=str)

    query = Expense.query.filter_by(user_id=current_user.id)
    if filter_status == 'paid':
        query = query.filter_by(is_paid=True)
    elif filter_status == 'unpaid':
        query = query.filter_by(is_paid=False)

    if date_from:
        query = query.filter(Expense.due_date >= date.fromisoformat(date_from))
    if date_to:
        query = query.filter(Expense.due_date <= date.fromisoformat(date_to))
    if category_id:
        query = query.filter_by(category_id=category_id)
    if amount_min is not None:
        query = query.filter(Expense.amount >= amount_min)
    if amount_max is not None:
        query = query.filter(Expense.amount <= amount_max)
    if search:
        query = query.filter(
            db.or_(
                Expense.description.ilike(f'%{search}%'),
                Expense.payee.ilike(f'%{search}%'),
            )
        )

    # Parcelas: mostrar apenas a proxima nao paga de cada parcelamento
    next_installment_sq = db.session.query(
        Expense.installment_id,
        func.min(Expense.installment_number).label('next_num')
    ).filter(
        Expense.user_id == current_user.id,
        Expense.installment_id.isnot(None),
        Expense.is_paid == False,
    ).group_by(Expense.installment_id).subquery()

    query = query.outerjoin(
        next_installment_sq,
        Expense.installment_id == next_installment_sq.c.installment_id
    ).filter(
        or_(
            Expense.installment_id.is_(None),
            Expense.is_paid == True,
            Expense.installment_number == next_installment_sq.c.next_num,
        )
    )

    expenses = query.order_by(Expense.due_date.desc()).paginate(page=page, per_page=10)
    categories = _get_expense_categories()
    filters = {
        'date_from': date_from, 'date_to': date_to,
        'category_id': category_id, 'amount_min': amount_min,
        'amount_max': amount_max, 'search': search,
    }
    return render_template('expenses/list.html',
        expenses=expenses, filter_status=filter_status,
        categories=categories, filters=filters)


@expenses_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = ExpenseForm()
    form.category_id.choices = _get_expense_categories()

    if form.validate_on_submit():
        expense = Expense(
            user_id=current_user.id,
            category_id=form.category_id.data,
            amount=form.amount.data,
            description=form.description.data,
            payee=form.payee.data,
            due_date=form.due_date.data,
            is_paid=form.is_paid.data,
            paid_date=date.today() if form.is_paid.data else None,
            is_recurring=form.is_recurring.data,
            recurrence=form.recurrence.data if form.is_recurring.data else None,
            priority=form.priority.data,
        )
        db.session.add(expense)
        db.session.commit()
        flash('Despesa adicionada com sucesso!', 'success')
        return redirect(url_for('transactions.list'))

    return render_template('expenses/form.html', form=form, title='Nova Despesa')


@expenses_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    expense = Expense.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = ExpenseForm(obj=expense)
    form.category_id.choices = _get_expense_categories()

    if form.validate_on_submit():
        expense.category_id = form.category_id.data
        expense.amount = form.amount.data
        expense.description = form.description.data
        expense.payee = form.payee.data
        expense.due_date = form.due_date.data
        expense.is_paid = form.is_paid.data
        expense.paid_date = date.today() if form.is_paid.data and not expense.paid_date else expense.paid_date
        expense.is_recurring = form.is_recurring.data
        expense.recurrence = form.recurrence.data if form.is_recurring.data else None
        expense.priority = form.priority.data
        # Sync category to installment and sibling expenses
        if expense.installment_id and expense.installment:
            expense.installment.category_id = form.category_id.data
            for sibling in expense.installment.expenses:
                sibling.category_id = form.category_id.data
        db.session.commit()
        flash('Despesa atualizada!', 'success')
        return redirect(url_for('transactions.list'))

    return render_template('expenses/form.html', form=form, title='Editar Despesa')


@expenses_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    expense = Expense.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(expense)
    db.session.commit()
    flash('Despesa removida.', 'success')
    return redirect(request.referrer or url_for('transactions.list'))


@expenses_bp.route('/toggle-paid/<int:id>', methods=['POST'])
@login_required
def toggle_paid(id):
    expense = Expense.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    expense.is_paid = not expense.is_paid
    expense.paid_date = date.today() if expense.is_paid else None
    db.session.commit()
    status = 'paga' if expense.is_paid else 'pendente'
    flash(f'Conta marcada como {status}.', 'success')
    return redirect(request.referrer or url_for('transactions.list'))


@expenses_bp.route('/export-csv')
@login_required
def export_csv():
    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.due_date.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Vencimento', 'Descricao', 'Categoria', 'Destinatario', 'Valor', 'Status', 'Prioridade'])
    for exp in expenses:
        writer.writerow([
            exp.due_date.strftime('%d/%m/%Y') if exp.due_date else '',
            exp.description or '',
            exp.category.name if exp.category else '',
            exp.payee or '',
            f'{exp.amount:.2f}',
            'Paga' if exp.is_paid else 'Pendente',
            exp.priority or 'normal',
        ])
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=despesas.csv'},
    )


def _get_expense_categories():
    cats = Category.query.filter(
        Category.type == 'expense',
        db.or_(Category.user_id == current_user.id, Category.user_id == None)
    ).all()
    return [(c.id, c.name) for c in cats]
