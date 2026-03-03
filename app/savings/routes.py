from datetime import date
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.savings import savings_bp
from app.savings.forms import SavingsGoalForm, ContributionForm
from app.extensions import db
from app.models.savings_goal import SavingsGoal
from app.models.savings_contribution import SavingsContribution


@savings_bp.route('/')
@login_required
def list():
    goals = SavingsGoal.query.filter_by(
        user_id=current_user.id
    ).order_by(SavingsGoal.is_completed, SavingsGoal.created_at.desc()).all()
    return render_template('savings/list.html', goals=goals)


@savings_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = SavingsGoalForm()
    if form.validate_on_submit():
        goal = SavingsGoal(
            user_id=current_user.id,
            name=form.name.data,
            target_amount=form.target_amount.data,
            deadline=form.deadline.data,
            icon=form.icon.data,
            color=form.color.data,
        )
        db.session.add(goal)
        db.session.commit()
        flash('Meta criada com sucesso!', 'success')
        return redirect(url_for('savings.list'))
    return render_template('savings/form.html', form=form, title='Nova Meta')


@savings_bp.route('/<int:id>')
@login_required
def detail(id):
    goal = SavingsGoal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    page = request.args.get('page', 1, type=int)
    contributions = goal.contributions.order_by(
        SavingsContribution.date.desc()
    ).paginate(page=page, per_page=10)
    return render_template('savings/detail.html', goal=goal, contributions=contributions)


@savings_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    goal = SavingsGoal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = SavingsGoalForm(obj=goal)
    if form.validate_on_submit():
        goal.name = form.name.data
        goal.target_amount = form.target_amount.data
        goal.deadline = form.deadline.data
        goal.icon = form.icon.data
        goal.color = form.color.data
        goal.is_completed = goal.current_amount >= goal.target_amount
        db.session.commit()
        flash('Meta atualizada!', 'success')
        return redirect(url_for('savings.detail', id=goal.id))
    return render_template('savings/form.html', form=form, title='Editar Meta')


@savings_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    goal = SavingsGoal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(goal)
    db.session.commit()
    flash('Meta removida.', 'success')
    return redirect(url_for('savings.list'))


@savings_bp.route('/<int:id>/contribute', methods=['GET', 'POST'])
@login_required
def contribute(id):
    goal = SavingsGoal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = ContributionForm()
    if request.method == 'GET':
        form.date.data = date.today()
    if form.validate_on_submit():
        contribution = SavingsContribution(
            goal_id=goal.id,
            amount=form.amount.data,
            description=form.description.data,
            date=form.date.data,
        )
        goal.current_amount = (goal.current_amount or 0) + form.amount.data
        if goal.current_amount >= goal.target_amount:
            goal.is_completed = True
        db.session.add(contribution)
        db.session.commit()
        flash('Contribuicao adicionada!', 'success')
        return redirect(url_for('savings.detail', id=goal.id))
    return render_template('savings/contribute.html', form=form, goal=goal)


@savings_bp.route('/contribution/<int:id>/delete', methods=['POST'])
@login_required
def delete_contribution(id):
    contribution = SavingsContribution.query.get_or_404(id)
    goal = SavingsGoal.query.filter_by(
        id=contribution.goal_id, user_id=current_user.id
    ).first_or_404()
    goal.current_amount = (goal.current_amount or 0) - contribution.amount
    if goal.current_amount < 0:
        goal.current_amount = 0
    goal.is_completed = goal.current_amount >= goal.target_amount
    db.session.delete(contribution)
    db.session.commit()
    flash('Contribuicao removida.', 'success')
    return redirect(url_for('savings.detail', id=goal.id))
