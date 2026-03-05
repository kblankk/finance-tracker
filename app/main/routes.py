from datetime import date, timedelta
from decimal import Decimal
from flask import render_template, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import func, extract, and_, or_
from app.main import main_bp
from app.extensions import db
from app.models.income import Income
from app.models.expense import Expense
from app.models.category import Category
from app.models.reminder import Reminder
from app.models.budget import Budget
from app.models.savings_goal import SavingsGoal
from app.models.savings_contribution import SavingsContribution


@main_bp.route('/')
@main_bp.route('/dashboard')
@login_required
def dashboard():
    today = date.today()
    first_day = today.replace(day=1)
    # Ultimo dia do mes
    if today.month == 12:
        last_day = today.replace(day=31)
    else:
        last_day = today.replace(month=today.month + 1, day=1) - timedelta(days=1)

    # Summary cards - mes inteiro (receitas e despesas planejadas)
    total_income = db.session.query(func.sum(Income.amount)).filter(
        Income.user_id == current_user.id,
        Income.date >= first_day,
        Income.date <= last_day,
    ).scalar() or Decimal('0')

    total_expenses = db.session.query(func.sum(Expense.amount)).filter(
        Expense.user_id == current_user.id,
        Expense.due_date >= first_day,
        Expense.due_date <= last_day,
    ).scalar() or Decimal('0')

    # Subquery: proxima parcela nao paga de cada parcelamento
    next_inst_sq = db.session.query(
        Expense.installment_id,
        func.min(Expense.installment_number).label('next_num')
    ).filter(
        Expense.user_id == current_user.id,
        Expense.installment_id.isnot(None),
        Expense.is_paid == False,
    ).group_by(Expense.installment_id).subquery()

    pending_bills = db.session.query(func.count(Expense.id)).outerjoin(
        next_inst_sq,
        Expense.installment_id == next_inst_sq.c.installment_id
    ).filter(
        Expense.user_id == current_user.id,
        Expense.is_paid == False,
        or_(
            Expense.installment_id.is_(None),
            Expense.installment_number == next_inst_sq.c.next_num,
        )
    ).scalar()

    # Depositos e saques em metas do mes
    savings_deposits = db.session.query(func.sum(SavingsContribution.amount)).join(
        SavingsGoal
    ).filter(
        SavingsGoal.user_id == current_user.id,
        SavingsContribution.date >= first_day,
        SavingsContribution.date <= last_day,
        db.or_(SavingsContribution.type == 'deposit', SavingsContribution.type == None),
    ).scalar() or Decimal('0')

    savings_withdrawals = db.session.query(func.sum(SavingsContribution.amount)).join(
        SavingsGoal
    ).filter(
        SavingsGoal.user_id == current_user.id,
        SavingsContribution.date >= first_day,
        SavingsContribution.date <= last_day,
        SavingsContribution.type == 'withdrawal',
    ).scalar() or Decimal('0')

    total_savings = savings_deposits - savings_withdrawals

    balance = total_income - total_expenses - total_savings

    # Upcoming bills (next 30 days, only next installment per group)
    upcoming = db.session.query(Expense).outerjoin(
        next_inst_sq,
        Expense.installment_id == next_inst_sq.c.installment_id
    ).filter(
        Expense.user_id == current_user.id,
        Expense.is_paid == False,
        Expense.due_date >= today,
        Expense.due_date <= today + timedelta(days=30),
        or_(
            Expense.installment_id.is_(None),
            Expense.installment_number == next_inst_sq.c.next_num,
        )
    ).order_by(Expense.due_date).limit(5).all()

    # Recent transactions
    recent_incomes = Income.query.filter_by(user_id=current_user.id).order_by(Income.date.desc()).limit(5).all()
    recent_expenses = Expense.query.filter_by(user_id=current_user.id).outerjoin(
        next_inst_sq,
        Expense.installment_id == next_inst_sq.c.installment_id
    ).filter(
        or_(
            Expense.installment_id.is_(None),
            Expense.installment_number == next_inst_sq.c.next_num,
        )
    ).order_by(Expense.created_at.desc()).limit(5).all()

    # Unread reminders count
    unread_count = Reminder.query.filter_by(user_id=current_user.id, is_read=False).count()

    # Budget alerts for current month
    budgets = Budget.query.filter_by(
        user_id=current_user.id, month=today.month, year=today.year
    ).all()
    budget_alerts = []
    for b in budgets:
        spent = db.session.query(func.sum(Expense.amount)).filter(
            Expense.user_id == current_user.id,
            Expense.category_id == b.category_id,
            extract('month', Expense.due_date) == today.month,
            extract('year', Expense.due_date) == today.year,
        ).scalar() or Decimal('0')
        pct = min(float(spent / b.amount_limit) * 100, 100) if b.amount_limit > 0 else 0
        budget_alerts.append({
            'category': b.category.name,
            'color': b.category.color or '#6c757d',
            'limit': b.amount_limit,
            'spent': spent,
            'pct': pct,
            'over': spent > b.amount_limit,
        })

    # Savings goals (top 3 active)
    savings_goals = SavingsGoal.query.filter_by(
        user_id=current_user.id, is_completed=False
    ).order_by(SavingsGoal.created_at.desc()).limit(3).all()

    return render_template('main/dashboard.html',
        total_income=total_income,
        total_expenses=total_expenses,
        total_savings=total_savings,
        balance=balance,
        pending_bills=pending_bills,
        upcoming=upcoming,
        recent_incomes=recent_incomes,
        recent_expenses=recent_expenses,
        unread_count=unread_count,
        budget_alerts=budget_alerts,
        savings_goals=savings_goals,
    )


@main_bp.route('/api/income-by-category')
@login_required
def api_income_by_category():
    today = date.today()
    first_day = today.replace(day=1)
    if today.month == 12:
        last_day = today.replace(day=31)
    else:
        last_day = today.replace(month=today.month + 1, day=1) - timedelta(days=1)

    results = db.session.query(
        Category.name, Category.color, func.sum(Income.amount)
    ).join(Income).filter(
        Income.user_id == current_user.id,
        Income.date >= first_day,
        Income.date <= last_day,
    ).group_by(Category.name, Category.color).all()

    return jsonify({
        'labels': [r[0] for r in results],
        'data': [float(r[2]) for r in results],
        'colors': [r[1] or '#6c757d' for r in results],
    })


@main_bp.route('/api/expense-by-category')
@login_required
def api_expense_by_category():
    """Distribuicao da receita: despesas por categoria + metas + saldo livre."""
    today = date.today()
    first_day = today.replace(day=1)
    if today.month == 12:
        last_day = today.replace(day=31)
    else:
        last_day = today.replace(month=today.month + 1, day=1) - timedelta(days=1)

    # Despesas por categoria
    results = db.session.query(
        Category.name, Category.color, func.sum(Expense.amount)
    ).join(Expense).filter(
        Expense.user_id == current_user.id,
        Expense.due_date >= first_day,
        Expense.due_date <= last_day,
    ).group_by(Category.name, Category.color).all()

    # Paleta quente para despesas no grafico de distribuicao
    expense_palette = [
        '#ea868f', '#e35d6a', '#dc3545', '#b02a37',
        '#f4a261', '#e76f51', '#e9967a', '#cd5c5c',
        '#ff7f50', '#d2691e', '#bc6c25', '#9b2226',
    ]

    labels = [r[0] for r in results]
    data = [float(r[2]) for r in results]
    colors = [expense_palette[i % len(expense_palette)] for i in range(len(results))]

    # Metas (depositos - saques do mes)
    savings_dep = db.session.query(func.sum(SavingsContribution.amount)).join(
        SavingsGoal
    ).filter(
        SavingsGoal.user_id == current_user.id,
        SavingsContribution.date >= first_day,
        SavingsContribution.date <= last_day,
        db.or_(SavingsContribution.type == 'deposit', SavingsContribution.type == None),
    ).scalar() or 0

    savings_wd = db.session.query(func.sum(SavingsContribution.amount)).join(
        SavingsGoal
    ).filter(
        SavingsGoal.user_id == current_user.id,
        SavingsContribution.date >= first_day,
        SavingsContribution.date <= last_day,
        SavingsContribution.type == 'withdrawal',
    ).scalar() or 0

    net_savings = float(savings_dep) - float(savings_wd)
    if net_savings > 0:
        labels.append('Metas')
        data.append(net_savings)
        colors.append('#0d6efd')

    # Saldo livre
    total_income = db.session.query(func.sum(Income.amount)).filter(
        Income.user_id == current_user.id,
        Income.date >= first_day,
        Income.date <= last_day,
    ).scalar() or 0

    used = sum(data)
    free = float(total_income) - used
    if free > 0:
        labels.append('Disponivel')
        data.append(free)
        colors.append('#20c997')

    return jsonify({
        'labels': labels,
        'data': data,
        'colors': colors,
    })


@main_bp.route('/api/monthly-trend')
@login_required
def api_monthly_trend():
    today = date.today()
    months = []
    income_data = []
    expense_data = []

    for i in range(5, -1, -1):
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12
            y -= 1

        month_income = db.session.query(func.sum(Income.amount)).filter(
            Income.user_id == current_user.id,
            extract('month', Income.date) == m,
            extract('year', Income.date) == y,
        ).scalar() or 0

        month_expense = db.session.query(func.sum(Expense.amount)).filter(
            Expense.user_id == current_user.id,
            extract('month', Expense.due_date) == m,
            extract('year', Expense.due_date) == y,
        ).scalar() or 0

        month_names = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        months.append(month_names[m - 1])
        income_data.append(float(month_income))
        expense_data.append(float(month_expense))

    return jsonify({
        'labels': months,
        'income': income_data,
        'expenses': expense_data,
    })
