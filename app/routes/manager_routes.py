from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity

from app.decorators import manager_required
from app.models import OrgUnit, User


manager_bp = Blueprint("manager_bp", __name__)


@manager_bp.get("/users")
@manager_required
def list_users_in_my_department():
    manager_id = int(get_jwt_identity())
    manager = User.query.get_or_404(manager_id)

    if manager.org_unit_id is None:
        return jsonify({"msg": "Manager chua duoc gan phong ban"}), 400

    # Include manager's org unit and all descendant units (teams under a department).
    unit_ids = {manager.org_unit_id}
    frontier = {manager.org_unit_id}

    while frontier:
        children = (
            OrgUnit.query.filter(OrgUnit.parent_id.in_(list(frontier)))
            .with_entities(OrgUnit.id)
            .all()
        )
        next_frontier = {c.id for c in children} - unit_ids
        if not next_frontier:
            break
        unit_ids.update(next_frontier)
        frontier = next_frontier

    users = (
        User.query.filter(
            User.org_unit_id.in_(list(unit_ids)),
            User.id != manager_id,
        )
        .order_by(User.id.desc())
        .all()
    )

    return jsonify(
        [
            {
                "id": u.id,
                "username": u.username,
                "full_name": u.full_name,
                "email": u.email,
                "phone": u.phone,
                "gender": u.gender,
                "birth_date": u.birth_date.isoformat() if u.birth_date else None,
                "job_title": u.job_title,
                "role": u.role.value,
                "org_unit_id": u.org_unit_id,
                "org_unit": u.org_unit.to_dict() if u.org_unit else None,
            }
            for u in users
        ]
    ), 200
