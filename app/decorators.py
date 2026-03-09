from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from app.models import User, UserRole


def get_current_user():
    """
    Get the current authenticated user object.
    Must be called after verify_jwt_in_request() or within @jwt_required() context.
    
    Returns: User object or None
    """
    try:
        identity = get_jwt_identity()
        if identity:
            return User.query.get(int(identity))
    except (TypeError, ValueError):
        pass
    return None


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        identity = get_jwt_identity()
        me = User.query.get(int(identity))
        if not me or me.role != UserRole.ADMIN:
            return jsonify({"msg": "Khong du quyen (admin)"}), 403
        return fn(*args, **kwargs)

    return wrapper


def manager_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        identity = get_jwt_identity()
        me = User.query.get(int(identity))
        if not me or me.role != UserRole.MANAGER:
            return jsonify({"msg": "Khong du quyen (manager)"}), 403
        return fn(*args, **kwargs)

    return wrapper
