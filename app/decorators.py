from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from app.models import User, UserRole


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
        if not me or me.role not in (UserRole.MANAGER, UserRole.ADMIN):
            return jsonify({"msg": "Khong du quyen (manager)"}), 403
        return fn(*args, **kwargs)

    return wrapper
