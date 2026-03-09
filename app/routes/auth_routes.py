from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models import User


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role.value},
        )
        return jsonify(
            {
                "status": "success",
                "access_token": access_token,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "full_name": user.full_name,
                    "role": user.role.value,
                },
            }
        ), 200

    return jsonify({"status": "error", "msg": "Invalid username or password"}), 401


@auth_bp.post("/logout")
@jwt_required()
def logout():
    # JWT is stateless, logout is handled client-side
    return jsonify({"msg": "Logged out"}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_profile():
    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({"msg": "Nguoi dung khong ton tai"}), 404

    return jsonify(
        {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "job_title": user.job_title,  # LEGACY field
            "job_title_id": user.job_title_id,  # NEW field
            "job_title_name": user.job_title_ref.name if user.job_title_ref else None,  # NEW field
            "email": user.email,
            "phone": user.phone,
            "org_unit": {"name": user.org_unit.name} if user.org_unit else None,
        }
    ), 200


@auth_bp.route("/change-password", methods=["PUT"])
@jwt_required()
def change_password():
    data = request.get_json() or {}
    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({"msg": "Nguoi dung khong ton tai"}), 404

    old_password = data.get("old_password")
    new_password = data.get("new_password")
    if not old_password or not new_password:
        return jsonify({"msg": "Thieu old_password hoac new_password"}), 400

    if not check_password_hash(user.password_hash, old_password):
        return jsonify({"msg": "Mat khau cu khong chinh xac"}), 400

    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    return jsonify({"msg": "Success"}), 200
