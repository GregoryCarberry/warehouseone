from functools import wraps
from flask import session, jsonify
from datetime import datetime
from . import db
from .models import Permission, UserPermission

def get_active_permissions(user_id):
    now = datetime.utcnow()
    q = db.session.query(Permission.name).join(UserPermission, Permission.permission_id == UserPermission.permission_id)        .filter(UserPermission.user_id == user_id)        .filter((UserPermission.valid_from == None) | (UserPermission.valid_from <= now))        .filter((UserPermission.valid_to == None) | (UserPermission.valid_to >= now))
    return {name for (name,) in q.all()}

def require_permission(permission_name):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            uid = session.get('user_id')
            if not uid:
                return jsonify({'error': 'unauthenticated'}), 401
            from .permissions import get_active_permissions
            perms = get_active_permissions(uid)
            if '*' in perms or permission_name in perms:
                return f(*args, **kwargs)
            return jsonify({'error': 'forbidden', 'missing_permission': permission_name}), 403
        return wrapper
    return decorator
