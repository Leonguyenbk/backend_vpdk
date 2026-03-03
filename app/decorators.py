from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, UserRole

def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        me = User.query.get(int(get_jwt_identity()))
        if not me or me.role != UserRole.ADMIN:
            return jsonify({"msg": "Không đủ quyền (admin)"}), 403
        return fn(*args, **kwargs)
    return wrapper