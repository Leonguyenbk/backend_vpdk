from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models import User, UserRole

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        identity = get_jwt_identity()
        me = User.query.get(int(identity))
        if not me or me.role != UserRole.ADMIN:
            return jsonify({"msg": "Không đủ quyền (admin)"}), 403
        return fn(*args, **kwargs)
    return wrapper