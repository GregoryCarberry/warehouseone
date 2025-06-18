from flask import Blueprint, request, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from .db import db
from .permissions import get_active_permissions

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            permissions = get_active_permissions(user)

            session['user_id'] = user.id
            session['username'] = user.username
            session['permissions'] = permissions

            return jsonify({
                'message': 'Login successful',
                'username': user.username,
                'permissions': permissions
            }), 200

        return jsonify({'error': 'Invalid credentials'}), 401

    except Exception as e:
        print("⚠️ Login Error:", str(e))
        return jsonify({'error': 'Internal server error'}), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'})
