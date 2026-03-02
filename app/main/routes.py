from datetime import date, timedelta
from decimal import Decimal
from flask import render_template, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import func, extract
from app.main import main_bp
from app.extensions import db
from app.models.income import Income
from app.models.expense import Expense
from app.models.category import Category
from app.models.reminder import Reminder


@main_bp.route('/')
@main_bp.route('/dashboard')
@login_required
def dashboard():
    today = date.today()
    first_day = today.replace(day=1)

    # Summary cards
    total_income = db.session.query(func.sum(Income.amount)).filter(
        Income.user_id == current_user.id,
        Income.date >= first_day,
        Income.date <= today,
    ).scalar() or Decimal('0')

    total_expenses = db.session.query(func.sum(Expense.amount)).filter(
        Expense.user_id == current_user.id,
        Expense.due_date >= first_day,
        Expense.due_date <= today,
    ).scalar() or Decimal('0')

    pending_bills = Expense.query.filter(
        Expense.user_id == current_user.id,
        Expense.is_paid == False,
        Expense.due_date >= today,
    ).count()

    balance = total_income - total_expenses

    # Upcoming bills (next 7 days)
    upcoming = Expense.query.filter(
        Expense.user_id == current_user.id,
        Expense.is_paid == False,
        Expense.due_date >= today,
        Expense.due_date <= today + timedelta(days=7),
    ).order_by(Expense.due_date).limit(5).all()

    # Recent transactions
    recent_incomes = Income.query.filter_by(user_id=current_user.id).order_by(Income.date.desc()).limit(5).all()
    recent_expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.created_at.desc()).limit(5).all()

    # Unread reminders count
    unread_count = Reminder.query.filter_by(user_id=current_user.id, is_read=False).count()

    return render_template('main/dashboard.html',
        total_income=total_income,
        total_expenses=total_expenses,
        balance=balance,
        pending_bills=pending_bills,
        upcoming=upcoming,
        recent_incomes=recent_incomes,
        recent_expenses=recent_expenses,
        unread_count=unread_count,
    )


@main_bp.route('/api/income-by-category')
@login_required
def api_income_by_category():
    today = date.today()
    first_day = today.replace(day=1)

    results = db.session.query(
        Category.name, Category.color, func.sum(Income.amount)
    ).join(Income).filter(
        Income.user_id == current_user.id,
        Income.date >= first_day,
    ).group_by(Category.name, Category.color).all()

    return jsonify({
        'labels': [r[0] for r in results],
        'data': [float(r[2]) for r in results],
        'colors': [r[1] or '#6c757d' for r in results],
    })


@main_bp.route('/api/expense-by-category')
@login_required
def api_expense_by_category():
    today = date.today()
    first_day = today.replace(day=1)

    results = db.session.query(
        Category.name, Category.color, func.sum(Expense.amount)
    ).join(Expense).filter(
        Expense.user_id == current_user.id,
        Expense.due_date >= first_day,
    ).group_by(Category.name, Category.color).all()

    return jsonify({
        'labels': [r[0] for r in results],
        'data': [float(r[2]) for r in results],
        'colors': [r[1] or '#6c757d' for r in results],
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
