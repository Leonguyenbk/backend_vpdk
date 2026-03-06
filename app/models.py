from datetime import datetime, timezone
from .extensions import db
import enum
from sqlalchemy import Enum

# Định nghĩa các quyền
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

    @classmethod
    def from_any(cls, raw_value):
        if isinstance(raw_value, cls):
            return raw_value
        if raw_value is None:
            raise ValueError("Role is required")

        value = str(raw_value).strip()
        if not value:
            raise ValueError("Role is required")

        # Accept both payload styles: "admin" and "ADMIN".
        try:
            return cls(value.lower())
        except ValueError:
            return cls[value.upper()]

# 1) ĐƠN VỊ / PHÒNG BAN / CHI NHÁNH (dạng cây)
class OrgUnit(db.Model):
    __tablename__ = "org_unit"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)

    # department / team / branch... tùy mày chuẩn hóa
    unit_type = db.Column(db.String(30), nullable=False, default="department")

    parent_id = db.Column(db.Integer, db.ForeignKey("org_unit.id"), nullable=True, index=True)

    # relationship cây (1-n tự tham chiếu)
    parent = db.relationship(
        "OrgUnit",
        remote_side=[id],
        backref=db.backref("children", lazy="dynamic")
    )

    is_active = db.Column(db.Boolean, nullable=False, default=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self, include_children=False, children_depth=1):
        """
        include_children:
          - False: chỉ trả node hiện tại (dùng cho list, dropdown, CRUD)
          - True : trả kèm children (dùng dựng cây)
        children_depth:
          - 1: chỉ children trực tiếp
          - 2+: sâu hơn
        """
        data = {
            "id": self.id,
            "name": self.name,
            "unit_type": self.unit_type,
            "parent_id": self.parent_id,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            # tiện cho UI hiển thị nhanh
            "children_count": self.children.count() if hasattr(self, "children") else 0,
        }

        if include_children:
            if children_depth is None or children_depth <= 0:
                data["children"] = []
            else:
                kids = self.children.order_by(OrgUnit.id.asc()).all()
                data["children"] = [
                    c.to_dict(include_children=True, children_depth=children_depth - 1)
                    for c in kids
                ]

        return data

# 2) DANH MỤC VỊ TRÍ VIỆC LÀM (toàn hệ thống)
class JobPosition(db.Model):
    __tablename__ = "job_position"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)

    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


# 3) GẮN VỊ TRÍ VIỆC LÀM VÀO TỪNG ĐƠN VỊ
class OrgUnitJobPosition(db.Model):
    __tablename__ = "org_unit_job_position"

    id = db.Column(db.Integer, primary_key=True)

    org_unit_id = db.Column(db.Integer, db.ForeignKey("org_unit.id"), nullable=False)
    job_position_id = db.Column(db.Integer, db.ForeignKey("job_position.id"), nullable=False)

    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # 1 đơn vị không được khai 2 lần cùng 1 vị trí
    __table_args__ = (
        db.UniqueConstraint("org_unit_id", "job_position_id", name="uq_orgunit_jobpos"),
    )
    org_unit = db.relationship("OrgUnit", lazy="joined")
    job_position = db.relationship("JobPosition", lazy="joined")

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # 👉 Gộp họ và tên, cho phép NULL
    full_name = db.Column(db.String(100), nullable=True) 
    
    gender = db.Column(db.String(10), nullable=True)
    birth_date = db.Column(db.Date, nullable=True)
    email = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)

    job_title = db.Column(db.String(100), nullable=True)
    org_unit_id = db.Column(db.Integer, db.ForeignKey("org_unit.id"), nullable=True)
    org_unit_job_position_id = db.Column(
        db.Integer, db.ForeignKey("org_unit_job_position.id"), nullable=True
    )

    role = db.Column(
        Enum(
            UserRole,
            # DB legacy enum stores names (ADMIN/USER...), while API uses values (admin/user...).
            values_callable=lambda enum_cls: [e.name for e in enum_cls]
        ),
        nullable=False,
        default=UserRole.USER
    )

    # Sử dụng timezone-aware datetime
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    org_unit = db.relationship("OrgUnit", foreign_keys=[org_unit_id], lazy="joined")
    org_unit_job_position = db.relationship("OrgUnitJobPosition", foreign_keys=[org_unit_job_position_id], lazy="joined")
