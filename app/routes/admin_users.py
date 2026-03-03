from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from app.extensions import db
from app.models import User, UserRole
from app.decorators import admin_required

admin_users_bp = Blueprint(
    "admin_users_bp",
    __name__,
    url_prefix="" # Để trống ở đây vì file khởi tạo app đã lo phần /api/admin/users rồi
)

@admin_users_bp.get("")
@admin_required
def list_users():
    users = User.query.order_by(User.id.desc()).all()
    return jsonify([
        {
            "id": u.id,
            "username": u.username,
            "full_name": u.full_name,
            "email": u.email,
            "role": u.role.value,
            "org_unit_id": u.org_unit_id,
            "is_active": u.is_active
        }
        for u in users
    ]), 200


@admin_users_bp.post("")
@admin_required
def create_user():
    data = request.get_json() or {}

    username = data.get("username")
    password = data.get("password")
    role = data.get("role", "user")

    if not username or not password:
        return jsonify({"msg": "Thiếu username hoặc password"}), 400

    if role not in ["admin", "manager", "user"]:
        return jsonify({"msg": "Role không hợp lệ"}), 400

    u = User(
        username=username,
        password_hash=generate_password_hash(password),
        role=UserRole(role),
        org_unit_id=data.get("org_unit_id")
    )

    db.session.add(u)
    db.session.commit()

    return jsonify({"msg": "created"}), 201