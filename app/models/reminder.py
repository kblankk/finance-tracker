from datetime import datetime
from app.extensions import db


class Reminder(db.Model):
    __tablename__ = 'reminders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    expense_id = db.Column(db.Integer, db.ForeignKey('expenses.id'), nullable=True)
    title = db.Column(db.String(128), nullable=False)
    message = db.Column(db.Text, nullable=True)
    remind_at = db.Column(db.DateTime, nullable=False, index=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Reminder {self.title}>'
