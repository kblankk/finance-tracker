from flask import jsonify, request
from flask_login import login_required, current_user
from app.categories import categories_bp
from app.extensions import db
from app.models.category import Category


@categories_bp.route('/api/categories', methods=['POST'])
@login_required
def create():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados invalidos'}), 400

    name = (data.get('name') or '').strip()
    cat_type = data.get('type')
    color = data.get('color', '#6c757d')
    icon = data.get('icon', 'bi-tag')

    if not name:
        return jsonify({'error': 'Nome e obrigatorio'}), 400
    if cat_type not in ('income', 'expense'):
        return jsonify({'error': 'Tipo invalido'}), 400

    existing = Category.query.filter_by(
        name=name, type=cat_type, user_id=current_user.id
    ).first()
    if existing:
        return jsonify({'error': 'Categoria ja existe'}), 400

    cat = Category(
        name=name,
        type=cat_type,
        color=color,
        icon=icon,
        is_default=False,
        user_id=current_user.id,
    )
    db.session.add(cat)
    db.session.commit()

    return jsonify({'id': cat.id, 'name': cat.name}), 201
