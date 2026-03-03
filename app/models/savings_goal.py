from datetime import datetime
from app.extensions import db


class SavingsGoal(db.Model):
    __tablename__ = 'savings_goals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(128), nullable=False)
    target_amount = db.Column(db.Numeric(12, 2), nullable=False)
    current_amount = db.Column(db.Numeric(12, 2), default=0)
    deadline = db.Column(db.Date, nullable=True)
    icon = db.Column(db.String(50), default='bi-piggy-bank')
    color = db.Column(db.String(7), default='#0d6efd')
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    contributions = db.relationship('SavingsContribution', backref='goal',
                                    lazy='dynamic', cascade='all, delete-orphan')

    @property
    def progress_pct(self):
        if not self.target_amount or self.target_amount <= 0:
            return 100
        return min(float(self.current_amount / self.target_amount) * 100, 100)

    def __repr__(self):
        return f'<SavingsGoal {self.name}>'
