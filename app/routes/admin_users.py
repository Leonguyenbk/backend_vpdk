from datetime import datetime

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import DataError
from werkzeug.security import generate_password_hash
from flask_jwt_extended import jwt_required

from app.decorators import admin_required, manager_required
from app.extensions import db
from app.models import JobTitle, OrgUnit, User, UserRole


admin_users_bp = Blueprint("admin_users_bp", __name__)


def parse_parent_id(data):
    if not data:
        return None

    pid = data.get("parent_id")
    if pid is None or pid == "":
        return None

    try:
        pid_int = int(pid)
    except (TypeError, ValueError):
        return None

    return None if pid_int == 0 else pid_int


def parse_birth_date(raw_value):
    if raw_value in (None, ""):
        return None
    if isinstance(raw_value, str):
        try:
            return datetime.strptime(raw_value.strip(), "%Y-%m-%d").date()
        except ValueError:
            return "__invalid__"
    return "__invalid__"


@admin_users_bp.get("/users")
@admin_required
def list_users():
    users = User.query.order_by(User.id.desc()).all()
    return (
        jsonify([u.to_dict() for u in users]),
        200,
    )


@admin_users_bp.get("/job-titles")
@admin_required
def list_job_titles():
    """
    API để lấy danh sách chức danh cho dropdown trong form chỉnh sửa user.
    Chỉ trả về các job_title đang active.
    """
    job_titles = JobTitle.query.filter_by(is_active=True).order_by(JobTitle.level_no.desc(), JobTitle.name.asc()).all()
    return jsonify([jt.to_dict() for jt in job_titles]), 200


@admin_users_bp.post("/users")
@admin_required
def create_user():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"msg": "Username va mat khau khong duoc trong"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "Username da ton tai"}), 400

    user = User(
        username=username,
        password_hash=generate_password_hash(password),
        full_name=data.get("full_name"),
        email=data.get("email"),
        role=UserRole.from_any(data.get("role", "user")),
    )

    # Handle job_title_id if provided
    if "job_title_id" in data and data.get("job_title_id"):
        try:
            job_title_id = int(data.get("job_title_id"))
            job_title = JobTitle.query.filter_by(id=job_title_id, is_active=True).first()
            if job_title:
                user.job_title_id = job_title_id
                user.job_title = job_title.name
                # Auto-set role based on job title
                if job_title.is_manager:
                    user.role = UserRole.MANAGER
        except (TypeError, ValueError):
            pass

    db.session.add(user)
    try:
        db.session.commit()
    except DataError:
        db.session.rollback()
        return jsonify({"msg": "Du lieu khong hop le hoac khong tuong thich schema DB"}), 400

    return jsonify({"msg": "Da tao user"}), 201


@admin_users_bp.put("/users/<int:user_id>")
@admin_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json() or {}

    user.full_name = data.get("full_name", user.full_name)
    user.email = data.get("email", user.email)
    user.phone = data.get("phone", user.phone)
    user.gender = data.get("gender", user.gender)
    user.job_title = data.get("job_title", user.job_title)

    # Xử lý job_title_id (mới) - cho dropdown selection
    if "job_title_id" in data:
        raw_job_title_id = data.get("job_title_id")
        if raw_job_title_id in (None, ""):
            user.job_title_id = None
        else:
            try:
                job_title_id = int(raw_job_title_id)
            except (TypeError, ValueError):
                return jsonify({"msg": "job_title_id khong hop le"}), 400
            
            # Validate job_title exists and is active
            job_title = JobTitle.query.filter_by(id=job_title_id, is_active=True).first()
            if not job_title:
                return jsonify({"msg": "Chuc danh khong ton tai hoac da bi vo hieu hoa"}), 400
            
            user.job_title_id = job_title_id
            # Update legacy job_title string from the job_title object
            user.job_title = job_title.name
            # Auto-set role based on job title ONLY if job_title has is_manager=True
            # Don't override ADMIN role
            if job_title.is_manager and user.role != UserRole.ADMIN:
                user.role = UserRole.MANAGER

    if "birth_date" in data:
        parsed_birth_date = parse_birth_date(data.get("birth_date"))
        if parsed_birth_date == "__invalid__":
            return jsonify({"msg": "birth_date phai dung dinh dang YYYY-MM-DD"}), 400
        user.birth_date = parsed_birth_date

    raw_role = data.get("role")
    if raw_role is not None:
        try:
            user.role = UserRole.from_any(raw_role)
        except ValueError:
            return jsonify({"msg": f"Role khong hop le: {raw_role}"}), 400

    if "org_unit_id" in data:
        raw_org_unit_id = data.get("org_unit_id")
        if raw_org_unit_id in (None, ""):
            user.org_unit_id = None
        else:
            try:
                org_unit_id = int(raw_org_unit_id)
            except (TypeError, ValueError):
                return jsonify({"msg": "org_unit_id khong hop le"}), 400
            if not OrgUnit.query.get(org_unit_id):
                return jsonify({"msg": "Don vi khong ton tai"}), 400
            user.org_unit_id = org_unit_id

    if hasattr(user, "is_active") and "is_active" in data:
        user.is_active = data.get("is_active", user.is_active)

    if data.get("password"):
        user.password_hash = generate_password_hash(data.get("password"))

    try:
        db.session.commit()
    except DataError:
        db.session.rollback()
        return jsonify({"msg": "Du lieu khong hop le hoac khong tuong thich schema DB"}), 400

    return jsonify({"msg": "Cap nhat thanh cong"}), 200


@admin_users_bp.delete("/users/<int:user_id>")
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"msg": "Da xoa user"}), 200


@admin_users_bp.get("/org-units")
@jwt_required()
def list_org_units():
    units = OrgUnit.query.order_by(OrgUnit.id.asc()).all()
    return jsonify([u.to_dict() for u in units]), 200


@admin_users_bp.post("/org-units")
@admin_required
def create_org_unit():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"msg": "Thieu ten don vi"}), 400

    parent_id = parse_parent_id(data)
    if parent_id is not None and not OrgUnit.query.get(parent_id):
        return jsonify({"msg": "Don vi cha khong ton tai"}), 400

    new_unit = OrgUnit(
        name=name,
        parent_id=parent_id,
        unit_type="team" if parent_id is not None else "department",
        is_active=True,
    )

    db.session.add(new_unit)
    db.session.commit()
    return jsonify(new_unit.to_dict()), 201


@admin_users_bp.put("/org-units/<int:id>")
@admin_required
def update_org_unit(id):
    unit = OrgUnit.query.get_or_404(id)
    data = request.get_json(silent=True) or {}

    if "name" in data:
        name = (data.get("name") or "").strip()
        if not name:
            return jsonify({"msg": "Ten don vi khong hop le"}), 400
        unit.name = name

    if "parent_id" in data:
        parent_id = parse_parent_id(data)
        if parent_id == unit.id:
            return jsonify({"msg": "parent_id khong hop le"}), 400
        if parent_id is not None and not OrgUnit.query.get(parent_id):
            return jsonify({"msg": "Don vi cha khong ton tai"}), 400
        unit.parent_id = parent_id
        unit.unit_type = "team" if parent_id is not None else "department"

    if "is_active" in data:
        unit.is_active = bool(data.get("is_active"))

    db.session.commit()
    return jsonify(unit.to_dict()), 200


@admin_users_bp.delete("/org-units/<int:id>")
@admin_required
def delete_org_unit(id):
    unit = OrgUnit.query.get_or_404(id)
    if OrgUnit.query.filter_by(parent_id=unit.id).count() > 0:
        return jsonify({"msg": "Khong the xoa: don vi dang co to con"}), 400

    db.session.delete(unit)
    db.session.commit()
    return jsonify({"msg": "Da xoa"}), 200
