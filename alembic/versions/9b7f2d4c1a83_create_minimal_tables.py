"""create minimal tables

Revision ID: 9b7f2d4c1a83
Revises: 016fab54b66f
Create Date: 2026-05-14 22:35:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "9b7f2d4c1a83"
down_revision: Union[str, None] = "016fab54b66f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    user_role_enum = postgresql.ENUM("super_admin", "user", name="user_role_enum", create_type=False)
    user_status_enum = postgresql.ENUM("active", "inactive", name="user_status_enum", create_type=False)
    activity_action_enum = postgresql.ENUM(
        "login",
        "logout",
        "failed_login",
        "create_user",
        "update_user",
        "deactivate_user",
        "change_password",
        "forgot_password",
        "reset_password",
        name="activity_action_enum",
        create_type=False,
    )

    user_role_enum.create(op.get_bind(), checkfirst=True)
    user_status_enum.create(op.get_bind(), checkfirst=True)
    activity_action_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", user_role_enum, nullable=False),
        sa.Column("status", user_status_enum, nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_created_by"), "users", ["created_by"], unique=False)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    op.create_table(
        "activity_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("actor_user_id", sa.Integer(), nullable=True),
        sa.Column("action", activity_action_enum, nullable=False),
        sa.Column("target_user_id", sa.Integer(), nullable=True),
        sa.Column("success", sa.Boolean(), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["target_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_activity_logs_actor_user_id"), "activity_logs", ["actor_user_id"], unique=False)
    op.create_index(op.f("ix_activity_logs_id"), "activity_logs", ["id"], unique=False)
    op.create_index(op.f("ix_activity_logs_target_user_id"), "activity_logs", ["target_user_id"], unique=False)

    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_password_reset_tokens_id"), "password_reset_tokens", ["id"], unique=False)
    op.create_index(op.f("ix_password_reset_tokens_token_hash"), "password_reset_tokens", ["token_hash"], unique=False)
    op.create_index(op.f("ix_password_reset_tokens_user_id"), "password_reset_tokens", ["user_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    user_role_enum = postgresql.ENUM("super_admin", "user", name="user_role_enum", create_type=False)
    user_status_enum = postgresql.ENUM("active", "inactive", name="user_status_enum", create_type=False)
    activity_action_enum = postgresql.ENUM(
        "login",
        "logout",
        "failed_login",
        "create_user",
        "update_user",
        "deactivate_user",
        "change_password",
        "forgot_password",
        "reset_password",
        name="activity_action_enum",
        create_type=False,
    )

    op.drop_index(op.f("ix_password_reset_tokens_user_id"), table_name="password_reset_tokens")
    op.drop_index(op.f("ix_password_reset_tokens_token_hash"), table_name="password_reset_tokens")
    op.drop_index(op.f("ix_password_reset_tokens_id"), table_name="password_reset_tokens")
    op.drop_table("password_reset_tokens")

    op.drop_index(op.f("ix_activity_logs_target_user_id"), table_name="activity_logs")
    op.drop_index(op.f("ix_activity_logs_id"), table_name="activity_logs")
    op.drop_index(op.f("ix_activity_logs_actor_user_id"), table_name="activity_logs")
    op.drop_table("activity_logs")

    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_index(op.f("ix_users_created_by"), table_name="users")
    op.drop_table("users")

    activity_action_enum.drop(op.get_bind(), checkfirst=True)
    user_status_enum.drop(op.get_bind(), checkfirst=True)
    user_role_enum.drop(op.get_bind(), checkfirst=True)
