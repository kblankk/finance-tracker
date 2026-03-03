from flask import Flask, redirect, url_for, request, render_template
from flask_login import current_user
from app.extensions import db, login_manager, migrate, bcrypt, csrf


def create_app(config_class='config.DevelopmentConfig'):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from app.auth import auth_bp
    from app.main import main_bp
    from app.income import income_bp
    from app.expenses import expenses_bp
    from app.admin import admin_bp
    from app.reminders import reminders_bp
    from app.installments import installments_bp
    from app.reports import reports_bp
    from app.budgets import budgets_bp
    from app.savings import savings_bp
    from app.profile import profile_bp
    from app.transactions import transactions_bp
    from app.categories import categories_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(income_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(reminders_bp)
    app.register_blueprint(installments_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(budgets_bp)
    app.register_blueprint(savings_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(categories_bp)

    # Redirect unapproved users
    @app.before_request
    def check_user_approved():
        if current_user.is_authenticated and not current_user.is_approved:
            allowed = ('auth.logout', 'auth.pending_approval', 'auth.check_approved', 'static')
            if request.endpoint not in allowed:
                return redirect(url_for('auth.pending_approval'))

    # Error handlers
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    return app
