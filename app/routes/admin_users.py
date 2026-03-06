from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import DataError
from app.extensions import db
from app.models import User, UserRole, OrgUnit
from app.decorators import admin_required

admin_users_bp = Blueprint("admin_users_bp", __name__)

def parse_parent_id(data):
    """
    Chuẩn hóa parent_id:
    - None / "" / thiếu -> None
    - 0 / "0" -> None (root)
    - "5"/5 -> 5
    """
    if not data:
        return None

    pid = data.get("parent_id", None)

    if pid is None or pid == "":
        return None

    try:
        pid_int = int(pid)
    except (ValueError, TypeError):
        return None

    if pid_int == 0:
        return None

    return pid_int

# [GET] Lấy danh sách user
@admin_users_bp.get("/users") # Đảm bảo đường dẫn này khớp với frontend gọi
@admin_required
def list_users():
    users = User.query.order_by(User.id.desc()).all()
    return jsonify([{
        "id": u.id,
        "username": u.username,
        "full_name": u.full_name,
        "email": u.email,
        "phone": u.phone,
        "gender": u.gender,
        "birth_date": u.birth_date.isoformat() if u.birth_date else None,
        "job_title": getattr(u, "job_title", None),
        "role": u.role.value,
        "is_active": getattr(u, "is_active", True),

        # ✅ trả luôn phòng ban để drawer dùng person.org_unit?.name
        "org_unit_id": u.org_unit_id,
        "org_unit": u.org_unit.to_dict() if getattr(u, "org_unit", None) else None,
    } for u in users]), 200

# [POST] Tạo user mới
@admin_users_bp.post("/users")
@admin_required
def create_user():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return jsonify({"msg": "Username và mật khẩu không được trống"}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "Username đã tồn tại"}), 400

    u = User(
        username=username,
        password_hash=generate_password_hash(password),
        full_name=data.get("full_name"),
        email=data.get("email"),
        role=UserRole.from_any(data.get("role", "user"))
    )
    db.session.add(u)
    try:
        db.session.commit()
    except DataError:
        db.session.rollback()
        return jsonify({"msg": "Role khong tuong thich voi schema DB hien tai. Hay chay migration moi nhat."}), 400
    return jsonify({"msg": "Đã tạo user"}), 201

# [PUT] Cập nhật user
@admin_users_bp.route("/users/<int:user_id>", methods=["PUT"])
@admin_required
def update_user(user_id):
    u = User.query.get_or_404(user_id)
    data = request.get_json() or {}

    # Cập nhật mọi trường có trong Model
    u.full_name = data.get("full_name", u.full_name)
    u.email = data.get("email", u.email)
    u.phone = data.get("phone", u.phone)
    u.gender = data.get("gender", u.gender)
    u.birth_date = data.get("birth_date", u.birth_date) # YYYY-MM-DD
    u.job_title = data.get("job_title", u.job_title)
    raw_role = data.get("role")
    if raw_role is not None:
        try:
            u.role = UserRole.from_any(raw_role)
        except ValueError:
            return jsonify({"msg": f"Role không hợp lệ: {raw_role}"}), 400
    u.org_unit_id = data.get("org_unit_id", u.org_unit_id)
    if hasattr(u, "is_active") and "is_active" in data:
        u.is_active = data.get("is_active", u.is_active)

    if data.get("password"):
        u.password_hash = generate_password_hash(data.get("password"))

    try:
        db.session.commit()
    except DataError:
        db.session.rollback()
        return jsonify({"msg": "Role khong tuong thich voi schema DB hien tai. Hay chay migration moi nhat."}), 400
    return jsonify({"msg": "Cập nhật thành công"}), 200

# [DELETE] Xóa user
@admin_users_bp.delete("/users/<int:user_id>")
@admin_required
def delete_user(user_id):
    u = User.query.get_or_404(user_id)
    db.session.delete(u)
    db.session.commit()
    return jsonify({"msg": "Đã xóa user"}), 200

@admin_users_bp.get("/org-units")
@admin_required
def list_org_units():
    units = OrgUnit.query.order_by(OrgUnit.id.asc()).all()
    return jsonify([u.to_dict() for u in units]), 200


@admin_users_bp.post("/org-units")
@admin_required
def create_org_unit():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"msg": "Thiếu tên đơn vị"}), 400

    parent_id = parse_parent_id(data)

    # Nếu có parent_id thì parent phải tồn tại
    if parent_id is not None:
        parent = OrgUnit.query.get(parent_id)
        if not parent:
            return jsonify({"msg": "Đơn vị cha không tồn tại"}), 400

    new_unit = OrgUnit(
        name=name,
        parent_id=parent_id,
        unit_type="team" if parent_id is not None else "department",
        is_active=True
    )

    db.session.add(new_unit)
    db.session.commit()

    # ✅ trả record vừa tạo
    return jsonify(new_unit.to_dict()), 201


@admin_users_bp.put("/org-units/<int:id>")
@admin_required
def update_org_unit(id):
    unit = OrgUnit.query.get_or_404(id)
    data = request.get_json(silent=True) or {}

    if "name" in data:
        name = (data.get("name") or "").strip()
        if not name:
            return jsonify({"msg": "Tên đơn vị không hợp lệ"}), 400
        unit.name = name

    if "parent_id" in data:
        parent_id = parse_parent_id(data)

        # không cho tự trỏ chính nó
        if parent_id == unit.id:
            return jsonify({"msg": "parent_id không hợp lệ"}), 400

        if parent_id is not None:
            parent = OrgUnit.query.get(parent_id)
            if not parent:
                return jsonify({"msg": "Đơn vị cha không tồn tại"}), 400

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

    # ✅ chặn xóa nếu còn tổ con
    if OrgUnit.query.filter_by(parent_id=unit.id).count() > 0:
        return jsonify({"msg": "Không thể xóa: đơn vị đang có tổ con"}), 400

    db.session.delete(unit)
    db.session.commit()
    return jsonify({"msg": "Đã xóa"}), 200
