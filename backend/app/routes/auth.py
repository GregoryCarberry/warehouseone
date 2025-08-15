from flask import Blueprint, request, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from .. import db
from ..models import User
from ..permissions import get_active_permissions

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')
    if not username or not password:
        return jsonify({'error': 'username and password required'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'invalid credentials'}), 401

    session.clear()
    session['user_id'] = user.user_id
    session['permissions'] = list(get_active_permissions(user.user_id))
    return jsonify({'ok': True, 'user': {'user_id': user.user_id, 'username': user.username}, 'permissions': session['permissions']})

@bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'ok': True})

@bp.route('/me', methods=['GET'])
def me():
    uid = session.get('user_id')
    if not uid:
        return jsonify({'user': None})
    perms = session.get('permissions', [])
    return jsonify({'user': {'user_id': uid}, 'permissions': perms})
