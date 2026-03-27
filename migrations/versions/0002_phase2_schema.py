"""Phase 2 schema: selected_model + cleared_at on users, rate_limits table

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("selected_model", sa.String(100), nullable=True))
    op.add_column("users", sa.Column("cleared_at", sa.DateTime(), nullable=True))

    op.create_table(
        "rate_limits",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("window_start", sa.DateTime(), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_rate_limits_user_id"), "rate_limits", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_rate_limits_user_id"), table_name="rate_limits")
    op.drop_table("rate_limits")
    op.drop_column("users", "cleared_at")
    op.drop_column("users", "selected_model")
