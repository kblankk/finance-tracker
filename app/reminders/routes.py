from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.reminders import reminders_bp
from app.extensions import db
from app.models.reminder import Reminder
from app.models.expense import Expense


@reminders_bp.route('/')
@login_required
def list():
    reminders = Reminder.query.filter_by(user_id=current_user.id).order_by(
        Reminder.is_read, Reminder.remind_at.desc()
    ).all()
    return render_template('reminders/list.html', reminders=reminders)


@reminders_bp.route('/mark-read/<int:id>', methods=['POST'])
@login_required
def mark_read(id):
    reminder = Reminder.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    reminder.is_read = True
    db.session.commit()
    flash('Lembrete marcado como lido.', 'success')
    return redirect(url_for('reminders.list'))


@reminders_bp.route('/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    Reminder.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    flash('Todos os lembretes marcados como lidos.', 'success')
    return redirect(url_for('reminders.list'))


@reminders_bp.route('/generate', methods=['POST'])
@login_required
def generate():
    """Manually generate reminders for upcoming unpaid bills."""
    today = datetime.utcnow().date()
    threshold = today + timedelta(days=3)

    upcoming = Expense.query.filter(
        Expense.user_id == current_user.id,
        Expense.is_paid == False,
        Expense.due_date <= threshold,
        Expense.due_date >= today,
    ).all()

    created = 0
    for bill in upcoming:
        existing = Reminder.query.filter_by(expense_id=bill.id, is_read=False).first()
        if not existing:
            reminder = Reminder(
                user_id=current_user.id,
                expense_id=bill.id,
                title=f'Conta proxima: {bill.description or bill.payee or "Sem descricao"}',
                message=f'R$ {bill.amount} vence em {bill.due_date.strftime("%d/%m/%Y")}',
                remind_at=datetime.utcnow(),
            )
            db.session.add(reminder)
            created += 1

    db.session.commit()
    flash(f'{created} lembrete(s) gerado(s).', 'success')
    return redirect(url_for('reminders.list'))


@reminders_bp.route('/api/unread-count')
@login_required
def api_unread_count():
    count = Reminder.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({'count': count})
