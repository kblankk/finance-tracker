from datetime import datetime
from flask_login import UserMixin
from app.extensions import db, bcrypt, login_manager


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user')
    is_approved = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    incomes = db.relationship('Income', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    expenses = db.relationship('Expense', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    categories = db.relationship('Category', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    reminders = db.relationship('Reminder', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    budgets = db.relationship('Budget', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    savings_goals = db.relationship('SavingsGoal', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    installments = db.relationship('Installment', backref='owner', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
