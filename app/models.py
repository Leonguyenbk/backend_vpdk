from datetime import datetime, timezone
from .extensions import db
import enum
from sqlalchemy import Enum

# Định nghĩa các quyền
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

# 1) ĐƠN VỊ / PHÒNG BAN / CHI NHÁNH (dạng cây)
class OrgUnit(db.Model):
    __tablename__ = "org_unit"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)

    # Loại đơn vị: branch / department / team (tùy bạn dùng)
    unit_type = db.Column(db.String(30), nullable=True)

    # Tạo cây tổ chức
    parent_id = db.Column(db.Integer, db.ForeignKey("org_unit.id"), nullable=True)

    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


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


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # 👉 Gộp họ và tên, cho phép NULL
    full_name = db.Column(db.String(100), nullable=True) 
    
    gender = db.Column(db.String(10), nullable=True)
    birth_date = db.Column(db.Date, nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=True)
    phone = db.Column(db.String(20), nullable=True)

    job_title = db.Column(db.String(100), nullable=True)
    org_unit_id = db.Column(db.Integer, db.ForeignKey("org_unit.id"), nullable=True)
    org_unit_job_position_id = db.Column(
        db.Integer, db.ForeignKey("org_unit_job_position.id"), nullable=True
    )

    role = db.Column(
        Enum(UserRole), 
        nullable=False, 
        default=UserRole.USER
    )
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # Sử dụng timezone-aware datetime
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    org_unit = db.relationship("OrgUnit", foreign_keys=[org_unit_id], lazy="joined")
    org_unit_job_position = db.relationship("OrgUnitJobPosition", foreign_keys=[org_unit_job_position_id], lazy="joined")