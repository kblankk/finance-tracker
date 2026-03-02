from app.extensions import db


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'income' or 'expense'
    icon = db.Column(db.String(50), nullable=True)
    color = db.Column(db.String(7), nullable=True)
    is_default = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    incomes = db.relationship('Income', backref='category', lazy='dynamic')
    expenses = db.relationship('Expense', backref='category', lazy='dynamic')

    __table_args__ = (
        db.UniqueConstraint('name', 'type', 'user_id', name='uq_category_name_type_user'),
    )

    def __repr__(self):
        return f'<Category {self.name} ({self.type})>'
