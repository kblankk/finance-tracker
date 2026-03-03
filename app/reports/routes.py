from datetime import date
from decimal import Decimal
from flask import render_template, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import func, extract
from app.reports import reports_bp
from app.extensions import db
from app.models.income import Income
from app.models.expense import Expense
from app.models.category import Category


@reports_bp.route('/')
@login_required
def monthly():
    today = date.today()
    month1 = request.args.get('month1', today.month, type=int)
    year1 = request.args.get('year1', today.year, type=int)
    # Previous month as default for comparison
    prev_month = today.month - 1 if today.month > 1 else 12
    prev_year = today.year if today.month > 1 else today.year - 1
    month2 = request.args.get('month2', prev_month, type=int)
    year2 = request.args.get('year2', prev_year, type=int)

    return render_template('reports/monthly.html',
        month1=month1, year1=year1, month2=month2, year2=year2)


@reports_bp.route('/api/comparison')
@login_required
def api_comparison():
    month1 = request.args.get('month1', type=int)
    year1 = request.args.get('year1', type=int)
    month2 = request.args.get('month2', type=int)
    year2 = request.args.get('year2', type=int)

    if not all([month1, year1, month2, year2]):
        return jsonify({'error': 'Missing parameters'}), 400

    def get_month_data(m, y):
        income = db.session.query(func.sum(Income.amount)).filter(
            Income.user_id == current_user.id,
            extract('month', Income.date) == m,
            extract('year', Income.date) == y,
        ).scalar() or Decimal('0')

        expense = db.session.query(func.sum(Expense.amount)).filter(
            Expense.user_id == current_user.id,
            extract('month', Expense.due_date) == m,
            extract('year', Expense.due_date) == y,
        ).scalar() or Decimal('0')

        by_category = db.session.query(
            Category.name, Category.color, func.sum(Expense.amount)
        ).join(Expense).filter(
            Expense.user_id == current_user.id,
            extract('month', Expense.due_date) == m,
            extract('year', Expense.due_date) == y,
        ).group_by(Category.name, Category.color).all()

        return {
            'income': float(income),
            'expense': float(expense),
            'balance': float(income - expense),
            'categories': [{'name': r[0], 'color': r[1] or '#6c757d', 'amount': float(r[2])} for r in by_category],
        }

    return jsonify({
        'month1': get_month_data(month1, year1),
        'month2': get_month_data(month2, year2),
    })


@reports_bp.route('/api/trend')
@login_required
def api_trend():
    today = date.today()
    months_count = request.args.get('months', 12, type=int)
    month_names = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

    labels = []
    income_data = []
    expense_data = []
    balance_data = []

    for i in range(months_count - 1, -1, -1):
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

        labels.append(f'{month_names[m - 1]}/{str(y)[2:]}')
        income_data.append(float(month_income))
        expense_data.append(float(month_expense))
        balance_data.append(float(month_income) - float(month_expense))

    return jsonify({
        'labels': labels,
        'income': income_data,
        'expenses': expense_data,
        'balance': balance_data,
    })
