from flask import render_template, redirect, url_for, flash
from flask_login import login_required
from app.admin import admin_bp
from app.admin.decorators import admin_required
from app.extensions import db
from app.models.user import User


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)


@admin_bp.route('/approve/<int:id>', methods=['POST'])
@login_required
@admin_required
def approve(id):
    user = User.query.get_or_404(id)
    user.is_approved = True
    db.session.commit()
    flash(f'Usuario {user.username} aprovado!', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/reject/<int:id>', methods=['POST'])
@login_required
@admin_required
def reject(id):
    user = User.query.get_or_404(id)
    if user.role == 'admin':
        flash('Nao e possivel remover um administrador.', 'danger')
        return redirect(url_for('admin.users'))
    db.session.delete(user)
    db.session.commit()
    flash(f'Usuario {user.username} removido.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/toggle-active/<int:id>', methods=['POST'])
@login_required
@admin_required
def toggle_active(id):
    user = User.query.get_or_404(id)
    if user.role == 'admin':
        flash('Nao e possivel desativar um administrador.', 'danger')
        return redirect(url_for('admin.users'))
    user.is_active = not user.is_active
    db.session.commit()
    status = 'ativado' if user.is_active else 'desativado'
    flash(f'Usuario {user.username} {status}.', 'success')
    return redirect(url_for('admin.users'))
