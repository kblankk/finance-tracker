from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.profile import profile_bp
from app.profile.forms import ChangeEmailForm, ChangePasswordForm
from app.extensions import db


@profile_bp.route('/profile')
@login_required
def settings():
    email_form = ChangeEmailForm(obj=current_user)
    password_form = ChangePasswordForm()
    return render_template('profile/settings.html', email_form=email_form, password_form=password_form)


@profile_bp.route('/profile/email', methods=['POST'])
@login_required
def change_email():
    email_form = ChangeEmailForm()
    password_form = ChangePasswordForm()

    if email_form.validate_on_submit():
        current_user.email = email_form.email.data
        db.session.commit()
        flash('Email atualizado com sucesso!', 'success')
        return redirect(url_for('profile.settings'))

    return render_template('profile/settings.html', email_form=email_form, password_form=password_form)


@profile_bp.route('/profile/password', methods=['POST'])
@login_required
def change_password():
    email_form = ChangeEmailForm(obj=current_user)
    password_form = ChangePasswordForm()

    if password_form.validate_on_submit():
        if not current_user.check_password(password_form.current_password.data):
            flash('Senha atual incorreta.', 'danger')
            return render_template('profile/settings.html', email_form=email_form, password_form=password_form)

        current_user.set_password(password_form.new_password.data)
        db.session.commit()
        flash('Senha alterada com sucesso!', 'success')
        return redirect(url_for('profile.settings'))

    return render_template('profile/settings.html', email_form=email_form, password_form=password_form)
