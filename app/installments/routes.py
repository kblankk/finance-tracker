from datetime import date
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.installments import installments_bp
from app.installments.forms import InstallmentForm
from app.extensions import db
from app.models.installment import Installment
from app.models.expense import Expense
from app.models.category import Category


@installments_bp.route('/')
@login_required
def list():
    installments = Installment.query.filter_by(
        user_id=current_user.id
    ).order_by(Installment.created_at.desc()).all()

    inst_data = []
    for inst in installments:
        paid = inst.expenses.filter_by(is_paid=True).count()
        total = inst.num_installments
        inst_data.append({
            'installment': inst,
            'paid': paid,
            'total': total,
            'pct': (paid / total * 100) if total > 0 else 0,
        })

    return render_template('installments/list.html', inst_data=inst_data)


@installments_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = InstallmentForm()
    form.category_id.choices = _get_expense_categories()

    if request.method == 'GET':
        form.start_date.data = date.today()

    if form.validate_on_submit():
        additional = form.additional_per_month.data or 0
        installment = Installment(
            user_id=current_user.id,
            description=form.description.data,
            total_amount=form.total_amount.data,
            num_installments=form.num_installments.data,
            additional_per_month=additional,
            category_id=form.category_id.data,
            payee=form.payee.data,
            start_date=form.start_date.data,
        )
        db.session.add(installment)
        db.session.flush()

        installment_amount = form.total_amount.data / form.num_installments.data
        monthly_total = round(installment_amount + additional, 2)
        current_date = form.start_date.data
        for i in range(1, form.num_installments.data + 1):
            expense = Expense(
                user_id=current_user.id,
                category_id=form.category_id.data,
                amount=monthly_total,
                description=f'{form.description.data} ({i}/{form.num_installments.data})',
                payee=form.payee.data,
                due_date=current_date,
                is_paid=False,
                priority='normal',
                installment_id=installment.id,
                installment_number=i,
            )
            db.session.add(expense)
            # Advance to next month safely
            month = current_date.month + 1
            year = current_date.year
            if month > 12:
                month = 1
                year += 1
            day = min(current_date.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
            current_date = current_date.replace(year=year, month=month, day=day)

        db.session.commit()
        msg = f'Parcelamento criado: {form.num_installments.data}x de R$ {installment_amount:.2f}'
        if additional > 0:
            msg += f' + R$ {additional:.2f} = R$ {monthly_total:.2f}/mes'
        flash(msg, 'success')
        return redirect(url_for('installments.list'))

    return render_template('installments/form.html', form=form, title='Novo Parcelamento')


@installments_bp.route('/<int:id>')
@login_required
def detail(id):
    installment = Installment.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    expenses = installment.expenses.order_by(Expense.installment_number).all()
    paid_count = sum(1 for e in expenses if e.is_paid)
    return render_template('installments/detail.html',
        installment=installment, expenses=expenses, paid_count=paid_count)


@installments_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    installment = Installment.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(installment)
    db.session.commit()
    flash('Parcelamento removido.', 'success')
    return redirect(url_for('installments.list'))


def _get_expense_categories():
    cats = Category.query.filter(
        Category.type == 'expense',
        db.or_(Category.user_id == current_user.id, Category.user_id == None)
    ).all()
    return [(c.id, c.name) for c in cats]
