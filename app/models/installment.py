from datetime import datetime
from app.extensions import db


class Installment(db.Model):
    __tablename__ = 'installments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    description = db.Column(db.String(256), nullable=False)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)
    num_installments = db.Column(db.Integer, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    payee = db.Column(db.String(128), nullable=True)
    additional_per_month = db.Column(db.Numeric(12, 2), default=0)
    start_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    category = db.relationship('Category', backref='installments')
    expenses = db.relationship('Expense', backref='installment', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Installment {self.description} {self.num_installments}x>'
