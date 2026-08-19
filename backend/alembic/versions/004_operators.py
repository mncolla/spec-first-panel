"""Alembic revision 004 — operators and sessions."""

import sqlalchemy as sa

from alembic import op

revision = "004_operators"
down_revision = "003_inquiries"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "operators",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("password_hash", sa.String(length=512), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(
        "uq_operators_one_admin",
        "operators",
        ["role"],
        unique=True,
        postgresql_where=sa.text("role = 'admin'"),
    )
    op.create_table(
        "sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("operator_id", sa.Uuid(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["operator_id"], ["operators.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sessions_operator_id", "sessions", ["operator_id"])


def downgrade() -> None:
    op.drop_index("uq_operators_one_admin", table_name="operators")
    op.drop_index("ix_sessions_operator_id", table_name="sessions")
    op.drop_table("sessions")
    op.drop_table("operators")
