from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import auth_bp
from app.auth.forms import LoginForm, RegisterForm
from app.extensions import db
from app.models.user import User


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login realizado com sucesso!', 'success')
            return redirect(next_page or url_for('main.dashboard'))
        flash('Email ou senha incorretos.', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            is_approved=False,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Conta criada! Aguarde a aprovacao do administrador.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Voce saiu da conta.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/pending-approval')
@login_required
def pending_approval():
    if current_user.is_approved:
        return redirect(url_for('main.dashboard'))
    return render_template('auth/pending.html')
