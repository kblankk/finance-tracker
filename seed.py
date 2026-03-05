"""Seed the database with default categories and an admin user."""
from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.category import Category

app = create_app()

DEFAULT_CATEGORIES = [
    # Income categories
    {'name': 'Salario', 'type': 'income', 'icon': 'bi-cash-stack', 'color': '#28a745'},
    {'name': 'Freelance', 'type': 'income', 'icon': 'bi-laptop', 'color': '#17a2b8'},
    {'name': 'Investimentos', 'type': 'income', 'icon': 'bi-graph-up-arrow', 'color': '#6f42c1'},
    {'name': 'Aluguel Recebido', 'type': 'income', 'icon': 'bi-house', 'color': '#20c997'},
    {'name': 'Presente', 'type': 'income', 'icon': 'bi-gift', 'color': '#e83e8c'},
    {'name': 'Outros (Receita)', 'type': 'income', 'icon': 'bi-three-dots', 'color': '#6c757d'},
    # Expense categories
    {'name': 'Moradia', 'type': 'expense', 'icon': 'bi-house-door', 'color': '#dc3545'},
    {'name': 'Energia/Agua/Gas', 'type': 'expense', 'icon': 'bi-lightning', 'color': '#fd7e14'},
    {'name': 'Mercado', 'type': 'expense', 'icon': 'bi-cart', 'color': '#ffc107'},
    {'name': 'Transporte', 'type': 'expense', 'icon': 'bi-car-front', 'color': '#007bff'},
    {'name': 'Saude', 'type': 'expense', 'icon': 'bi-heart-pulse', 'color': '#e83e8c'},
    {'name': 'Educacao', 'type': 'expense', 'icon': 'bi-book', 'color': '#6f42c1'},
    {'name': 'Lazer', 'type': 'expense', 'icon': 'bi-controller', 'color': '#20c997'},
    {'name': 'Assinaturas', 'type': 'expense', 'icon': 'bi-tv', 'color': '#17a2b8'},
    {'name': 'Alimentacao Fora', 'type': 'expense', 'icon': 'bi-cup-hot', 'color': '#fd7e14'},
    {'name': 'Roupas', 'type': 'expense', 'icon': 'bi-bag', 'color': '#6610f2'},
    {'name': 'Dividas', 'type': 'expense', 'icon': 'bi-credit-card', 'color': '#dc3545'},
    {'name': 'Outros (Despesa)', 'type': 'expense', 'icon': 'bi-three-dots', 'color': '#6c757d'},
]


def seed():
    with app.app_context():
        # Create admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='kawabrein@gmail.com',
                role='admin',
                is_approved=True,
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print('Admin criado: admin / admin123')
        else:
            print('Admin ja existe.')

        # Create default categories
        created = 0
        for cat_data in DEFAULT_CATEGORIES:
            exists = Category.query.filter_by(
                name=cat_data['name'],
                type=cat_data['type'],
                user_id=None,
            ).first()
            if not exists:
                cat = Category(is_default=True, user_id=None, **cat_data)
                db.session.add(cat)
                created += 1

        db.session.commit()
        print(f'{created} categorias padrao criadas.')


if __name__ == '__main__':
    seed()
