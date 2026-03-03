from flask import render_template, redirect, url_for, flash
from flask_login import login_required
from app.admin import admin_bp
from app.admin.decorators import admin_required
from app.admin.forms import EditUserForm, ResetPasswordForm
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


@admin_bp.route('/edit-user/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    form = EditUserForm(original_user=user, obj=user)
    password_form = ResetPasswordForm()

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data
        db.session.commit()
        flash(f'Usuario {user.username} atualizado!', 'success')
        return redirect(url_for('admin.users'))

    return render_template('admin/edit_user.html', form=form, password_form=password_form, user=user)


@admin_bp.route('/reset-password/<int:id>', methods=['POST'])
@login_required
@admin_required
def reset_password(id):
    user = User.query.get_or_404(id)
    password_form = ResetPasswordForm()

    if password_form.validate_on_submit():
        user.set_password(password_form.new_password.data)
        db.session.commit()
        flash(f'Senha de {user.username} resetada com sucesso!', 'success')
        return redirect(url_for('admin.edit_user', id=user.id))

    form = EditUserForm(original_user=user, obj=user)
    return render_template('admin/edit_user.html', form=form, password_form=password_form, user=user)
