"""update org_unit relations and defaults

Revision ID: 734c639270e6
Revises: bcdb86078906
Create Date: 2026-03-04 08:56:34.355162

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '734c639270e6'
down_revision = 'bcdb86078906'
branch_labels = None
depends_on = None


from alembic import op
import sqlalchemy as sa

def upgrade():
    # 1) Thêm cột cho phép NULL để không bị zero-date
    op.add_column("org_unit", sa.Column("updated_at", sa.DateTime(), nullable=True))

    # 2) Set giá trị cho data cũ (lấy created_at nếu có, không thì NOW())
    op.execute("""
        UPDATE org_unit
        SET updated_at = COALESCE(created_at, NOW())
        WHERE updated_at IS NULL
    """)

    # 3) Đổi sang NOT NULL
    op.alter_column("org_unit", "updated_at", existing_type=sa.DateTime(), nullable=False)

    # 4) (Optional nhưng rất nên) đặt default + on update ở DB level
    # Alembic/SQLAlchemy không luôn map onupdate chuẩn cho MySQL,
    # nên dùng SQL trực tiếp:
    op.execute("""
        ALTER TABLE org_unit
        MODIFY updated_at DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
    """)

def downgrade():
    op.drop_column("org_unit", "updated_at")
