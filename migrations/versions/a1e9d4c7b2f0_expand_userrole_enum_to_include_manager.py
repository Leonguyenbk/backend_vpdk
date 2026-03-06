"""expand userrole enum to include manager

Revision ID: a1e9d4c7b2f0
Revises: f9a8c29bedfc
Create Date: 2026-03-06 10:05:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "a1e9d4c7b2f0"
down_revision = "f9a8c29bedfc"
branch_labels = None
depends_on = None


def upgrade():
    # Normalize old values before altering enum definition.
    op.execute("UPDATE user SET role = UPPER(role)")
    op.execute("UPDATE user SET role = 'USER' WHERE role NOT IN ('ADMIN', 'MANAGER', 'USER')")
    op.execute("ALTER TABLE user MODIFY role ENUM('ADMIN','MANAGER','USER') NOT NULL")


def downgrade():
    # MANAGER is not available in the old enum, map it back to USER.
    op.execute("UPDATE user SET role = 'USER' WHERE role = 'MANAGER'")
    op.execute("ALTER TABLE user MODIFY role ENUM('ADMIN','USER') NOT NULL")
