from flask import session, jsonify
from functools import wraps
from datetime import datetime

from .db import db
from sqlalchemy import and_, or_
from warehouse.models import user_permissions, Permission

def get_active_permissions(user):
    now = datetime.utcnow()
    results = db.session.query(Permission.name).join(user_permissions).filter(
        user_permissions.c.user_id == user.id,
        and_(
            user_permissions.c.valid_from <= now,
            or_(user_permissions.c.valid_to == None, user_permissions.c.valid_to >= now)
        )
    ).all()

    return [name for (name,) in results]



def require_permission(permission):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'permissions' not in session or permission not in session['permissions']:
                return jsonify({'error': 'Forbidden'}), 403
            return func(*args, **kwargs)
        return wrapper
    return decorator

def register_permission_hooks(app):
    @app.before_request
    def load_permissions():
        if 'user_id' in session and 'permissions' not in session:
            from .models import User
            user = User.query.get(session['user_id'])
            session['permissions'] = get_active_permissions(user)
