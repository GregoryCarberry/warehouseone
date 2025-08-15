from flask import Blueprint, jsonify, request
from .. import db
from ..models import User, Permission, UserPermission
from ..permissions import require_permission

bp = Blueprint('admin', __name__)

@bp.route('/users', methods=['GET'])
@require_permission('view_users')
def list_users():
    users = User.query.all()
    return jsonify([{'user_id': u.user_id, 'username': u.username} for u in users])

@bp.route('/permissions', methods=['GET'])
@require_permission('view_permissions')
def list_permissions():
    perms = Permission.query.all()
    return jsonify([{'permission_id': p.permission_id, 'name': p.name, 'description': p.description} for p in perms])

@bp.route('/grant', methods=['POST'])
@require_permission('grant_permissions')
def grant_permission():
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    perm_name = data.get('permission')

    if not username or not perm_name:
        return {'error': 'username and permission are required'}, 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return {'error': 'user not found'}, 404

    perm = Permission.query.filter_by(name=perm_name).first()
    if not perm:
        return {'error': 'permission not found'}, 404

    up = UserPermission(user_id=user.user_id, permission_id=perm.permission_id)
    db.session.add(up)
    db.session.commit()
    return {'ok': True}
