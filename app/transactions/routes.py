import re
from datetime import date
from flask import render_template, request
from flask_login import login_required, current_user
from app.transactions import transactions_bp
from app.extensions import db
from app.models.income import Income
from app.models.expense import Expense
from app.models.category import Category
from app.models.savings_goal import SavingsGoal
from app.models.savings_contribution import SavingsContribution


@transactions_bp.route('/lancamentos')
@login_required
def list():
    page = request.args.get('page', 1, type=int)
    filter_type = request.args.get('type', 'all')
    date_from = request.args.get('date_from', type=str)
    date_to = request.args.get('date_to', type=str)
    category_id = request.args.get('category_id', type=int)
    amount_min = request.args.get('amount_min', type=float)
    amount_max = request.args.get('amount_max', type=float)
    search = request.args.get('search', type=str)
    per_page = 15

    items = []

    # Receitas
    if filter_type in ('all', 'income'):
        q = Income.query.filter_by(user_id=current_user.id)
        if date_from:
            q = q.filter(Income.date >= date.fromisoformat(date_from))
        if date_to:
            q = q.filter(Income.date <= date.fromisoformat(date_to))
        if category_id:
            q = q.filter_by(category_id=category_id)
        if amount_min is not None:
            q = q.filter(Income.amount >= amount_min)
        if amount_max is not None:
            q = q.filter(Income.amount <= amount_max)
        if search:
            q = q.filter(db.or_(
                Income.description.ilike(f'%{search}%'),
                Income.source.ilike(f'%{search}%'),
            ))
        for inc in q.all():
            items.append({
                'type': 'income',
                'id': inc.id,
                'date': inc.date,
                'description': inc.description or inc.source or 'Receita',
                'category': inc.category,
                'detail': inc.source or '',
                'amount': float(inc.amount),
                'is_paid': None,
                'is_received': getattr(inc, 'is_received', False),
                'installment_info': None,
            })

    # Despesas (só mostra parcela 1 de cada parcelamento)
    if filter_type in ('all', 'expense'):
        q = Expense.query.filter_by(user_id=current_user.id)
        q = q.filter(db.or_(
            Expense.installment_id == None,
            Expense.installment_number == 1,
        ))
        if date_from:
            q = q.filter(Expense.due_date >= date.fromisoformat(date_from))
        if date_to:
            q = q.filter(Expense.due_date <= date.fromisoformat(date_to))
        if category_id:
            q = q.filter_by(category_id=category_id)
        if amount_min is not None:
            q = q.filter(Expense.amount >= amount_min)
        if amount_max is not None:
            q = q.filter(Expense.amount <= amount_max)
        if search:
            q = q.filter(db.or_(
                Expense.description.ilike(f'%{search}%'),
                Expense.payee.ilike(f'%{search}%'),
            ))
        for exp in q.all():
            inst_info = None
            desc = exp.description or exp.payee or 'Despesa'
            if exp.installment_id and exp.installment:
                inst = exp.installment
                paid = sum(1 for e in inst.expenses if e.is_paid)
                inst_info = f'{paid}/{inst.num_installments} pagas'
                desc = re.sub(r'\s*\(\d+/\d+\)\s*$', '', desc)
            items.append({
                'type': 'expense',
                'id': exp.id,
                'date': exp.due_date,
                'description': desc,
                'category': exp.category,
                'detail': exp.payee or '',
                'amount': float(exp.amount),
                'is_paid': exp.is_paid,
                'installment_info': inst_info,
            })

    # Metas (depósitos e saques)
    if filter_type in ('all', 'savings'):
        q = SavingsContribution.query.join(SavingsGoal).filter(
            SavingsGoal.user_id == current_user.id
        )
        if date_from:
            q = q.filter(SavingsContribution.date >= date.fromisoformat(date_from))
        if date_to:
            q = q.filter(SavingsContribution.date <= date.fromisoformat(date_to))
        if amount_min is not None:
            q = q.filter(SavingsContribution.amount >= amount_min)
        if amount_max is not None:
            q = q.filter(SavingsContribution.amount <= amount_max)
        if search:
            q = q.filter(db.or_(
                SavingsContribution.description.ilike(f'%{search}%'),
                SavingsGoal.name.ilike(f'%{search}%'),
            ))
        for sc in q.all():
            is_deposit = sc.type != 'withdrawal'
            items.append({
                'type': 'savings',
                'id': sc.id,
                'date': sc.date,
                'description': sc.description or sc.goal.name,
                'category': None,
                'goal_name': sc.goal.name,
                'goal_color': sc.goal.color or '#0d6efd',
                'goal_icon': sc.goal.icon or 'bi bi-piggy-bank',
                'detail': 'Depósito' if is_deposit else 'Saque',
                'amount': float(sc.amount),
                'is_deposit': is_deposit,
                'is_paid': None,
                'is_received': None,
                'installment_info': None,
            })

    # Ordenar por data decrescente
    items.sort(key=lambda x: x['date'] or date.min, reverse=True)

    # Paginacao manual
    total = len(items)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = min(page, total_pages)
    start = (page - 1) * per_page
    page_items = items[start:start + per_page]

    # Categorias para o filtro
    categories = Category.query.filter(
        db.or_(Category.user_id == current_user.id, Category.user_id == None)
    ).order_by(Category.type, Category.name).all()
    cat_choices = [(c.id, f'{c.name} ({("Receita" if c.type == "income" else "Despesa")})') for c in categories]

    filters = {
        'type': filter_type,
        'date_from': date_from, 'date_to': date_to,
        'category_id': category_id, 'amount_min': amount_min,
        'amount_max': amount_max, 'search': search,
    }

    pagination = {
        'page': page, 'total_pages': total_pages,
        'has_prev': page > 1, 'has_next': page < total_pages,
        'prev_num': page - 1, 'next_num': page + 1,
        'total': total,
    }

    return render_template('transactions/list.html',
        items=page_items, categories=cat_choices,
        filters=filters, pagination=pagination)
